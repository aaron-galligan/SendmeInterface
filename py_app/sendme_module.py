import os
import sys
import asyncio
import random
import argparse
from pathlib import Path
from iroh_ffi import Iroh, BlobFormat, Hash, NodeAddr, RelayMode, SecretKey, BlobTicket, Collection, ImportProgress, DownloadProgress

# Helper function to print hash in different formats
def print_hash(hash: Hash, format: str) -> str:
    if format == "hex":
        return hash.to_hex()
    elif format == "cid":
        return hash.to_cid()
    else:
        raise ValueError("Invalid format")

# Function to get or create a secret key
def get_or_create_secret(print_key: bool) -> SecretKey:
    secret = os.getenv("IROH_SECRET")
    if secret:
        return SecretKey.from_str(secret)
    else:
        key = SecretKey.generate()
        if print_key:
            print(f"Using secret key: {key}")
        return key

# Function to validate path components
def validate_path_component(component: str) -> None:
    if '/' in component:
        raise ValueError("Path components must not contain '/'")

# Function to convert a canonicalized path to a string
def canonicalized_path_to_string(path: Path, must_be_relative: bool) -> str:
    parts = []
    for component in path.parts:
        if component == os.path.sep:
            if must_be_relative:
                raise ValueError("Invalid path component")
            continue
        validate_path_component(component)
        parts.append(component)
    return '/'.join(parts)

# Function to show ingest progress
async def show_ingest_progress(recv: asyncio.Queue) -> None:
    while True:
        progress = await recv.get()
        if isinstance(progress, ImportProgress.Found):
            print(f"Found: {progress.name}")
        elif isinstance(progress, ImportProgress.Size):
            print(f"Size: {progress.size}")
        elif isinstance(progress, ImportProgress.OutboardProgress):
            print(f"Progress: {progress.offset}")
        elif isinstance(progress, ImportProgress.OutboardDone):
            print("Outboard done")
        elif isinstance(progress, ImportProgress.CopyProgress):
            print("Copy progress")
        else:
            break

# Function to import files into the database
async def import(path: Path, db) -> tuple:
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")
    
    root = path.parent
    files = [f for f in path.rglob('*') if f.is_file()]
    data_sources = []
    for file in files:
        relative = file.relative_to(root)
        name = canonicalized_path_to_string(relative, True)
        data_sources.append((name, file))
    
    recv = asyncio.Queue()
    progress = AsyncChannelProgressSender(recv)
    show_progress_task = asyncio.create_task(show_ingest_progress(recv))
    
    names_and_tags = []
    for name, file_path in data_sources:
        temp_tag, file_size = await db.import_file(file_path, ImportMode.TryReference, BlobFormat.Raw, progress)
        names_and_tags.append((name, temp_tag, file_size))
    
    await show_progress_task
    names_and_tags.sort(key=lambda x: x[0])
    
    total_size = sum(size for _, _, size in names_and_tags)
    collection = Collection()
    tags = []
    for name, tag, _ in names_and_tags:
        collection.add(name, tag.hash())
        tags.append(tag)
    
    temp_tag = await collection.store(db)
    for tag in tags:
        tag.drop()
    
    return temp_tag, total_size, collection

# Function to export files from the database
async def export(db, collection: Collection) -> None:
    root = Path.cwd()
    for name, hash in collection.iter():
        target = root / name
        if target.exists():
            print(f"Target {target} already exists. Export stopped.")
            return
        await db.export(hash, target, ExportMode.TryReference, lambda _: None)

# Function to send files
async def send(args) -> None:
    secret_key = get_or_create_secret(args.verbose > 0)
    builder = Iroh.Endpoint.builder()
        .alpns([b"iroh-blobs"])
        .secret_key(secret_key)
        .relay_mode(RelayMode.from_str(args.relay))
    
    if args.ticket_type == "id":
        builder = builder.add_discovery(lambda sk: PkarrPublisher.n0_dns(sk))
    
    if args.magic_ipv4_addr:
        builder = builder.bind_addr_v4(args.magic_ipv4_addr)
    if args.magic_ipv6_addr:
        builder = builder.bind_addr_v6(args.magic_ipv6_addr)
    
    suffix = random.randbytes(16).hex()
    cwd = Path.cwd()
    blobs_data_dir = cwd / f".sendme-send-{suffix}"
    if blobs_data_dir.exists():
        print(f"Cannot share twice from the same directory: {cwd}")
        sys.exit(1)
    
    blobs_data_dir.mkdir(parents=True, exist_ok=True)
    endpoint = await builder.bind()
    blobs = await Blobs.persistent(blobs_data_dir).events(ClientStatus().into()).build(endpoint)
    
    router = await Iroh.Router.builder(endpoint)
        .accept(b"iroh-blobs", blobs)
        .spawn()
    
    path = Path(args.path)
    temp_tag, size, collection = await import(path, blobs.store())
    hash = temp_tag.hash()
    
    await router.endpoint().home_relay().initialized()
    addr = await router.endpoint().node_addr()
    apply_options(addr, args.ticket_type)
    ticket = BlobTicket.new(addr, hash, BlobFormat.HashSeq)
    
    entry_type = "file" if path.is_file() else "directory"
    print(f"Imported {entry_type} {path}, {size}, hash {print_hash(hash, args.format)}")
    if args.verbose > 0:
        for name, hash in collection.iter():
            print(f"    {print_hash(hash, args.format)} {name}")
    print(f"To get this data, use: sendme receive {ticket}")
    
    temp_tag.drop()
    await asyncio.get_event_loop().run_in_executor(None, input, "Press Enter to exit...")
    await router.shutdown()
    await blobs_data_dir.rmdir()

# Function to receive files
async def receive(args) -> None:
    ticket = args.ticket
    addr = ticket.node_addr()
    secret_key = get_or_create_secret(args.verbose > 0)
    builder = Iroh.Endpoint.builder()
        .alpns([])
        .secret_key(secret_key)
        .relay_mode(RelayMode.from_str(args.relay))
    
    if not addr.relay_url and not addr.direct_addresses:
        builder = builder.add_discovery(lambda _: DnsDiscovery.n0_dns())
    
    if args.magic_ipv4_addr:
        builder = builder.bind_addr_v4(args.magic_ipv4_addr)
    if args.magic_ipv6_addr:
        builder = builder.bind_addr_v6(args.magic_ipv6_addr)
    
    endpoint = await builder.bind()
    dir_name = f".sendme-get-{ticket.hash().to_hex()}"
    iroh_data_dir = Path.cwd() / dir_name
    db = await Iroh.Store.fs.load(iroh_data_dir)
    
    connection = await endpoint.connect(addr, b"iroh-blobs")
    hash_and_format = HashAndFormat(ticket.hash(), ticket.format())
    
    send, recv = asyncio.Queue(), asyncio.Queue()
    progress = AsyncChannelProgressSender(send)
    hash_seq, sizes = await get_hash_seq_and_sizes(connection, hash_and_format.hash, 32 * 1024 * 1024)
    total_size = sum(sizes)
    total_files = len(sizes) - 1
    payload_size = sum(sizes[1:])
    
    print(f"Getting collection {print_hash(ticket.hash(), args.format)} {total_files} files, {payload_size}")
    if args.verbose > 0:
        print(f"Getting {len(sizes)} blobs in total, {total_size}")
    
    download_task = asyncio.create_task(show_download_progress(recv, total_size))
    stats = await get_to_db(db, lambda: connection, hash_and_format, progress)
    collection = await Collection.load_db(db, hash_and_format.hash)
    
    if args.verbose > 0:
        for name, hash in collection.iter():
            print(f"    {print_hash(hash, args.format)} {name}")
    
    if collection.iter():
        first_name = next(collection.iter())[0]
        print(f"Downloading to: {first_name}")
    
    await export(db, collection)
    await iroh_data_dir.rmdir()
    
    if args.verbose > 0:
        print(f"Downloaded {total_files} files, {payload_size}. Took {stats.elapsed} ({stats.bytes_read / stats.elapsed.total_seconds()} bytes/s)")

# Main function
async def main():
    parser = argparse.ArgumentParser(description="Send and receive files using Iroh.")
    subparsers = parser.add_subparsers(dest="command")
    
    send_parser = subparsers.add_parser("send", help="Send a file or directory.")
    send_parser.add_argument("path", type=Path, help="Path to the file or directory to send.")
    send_parser.add_argument("--ticket-type", default="relay_and_addresses", choices=["id", "relay_and_addresses", "relay", "addresses"], help="Type of ticket to use.")
    send_parser.add_argument("--magic-ipv4-addr", type=str, help="IPv4 address to bind to.")
    send_parser.add_argument("--magic-ipv6-addr", type=str, help="IPv6 address to bind to.")
    send_parser.add_argument("--format", default="hex", choices=["hex", "cid"], help="Format to display hashes.")
    send_parser.add_argument("--verbose", action="count", default=0, help="Increase verbosity.")
    send_parser.add_argument("--relay", default="default", choices=["disabled", "default", "custom"], help="Relay mode to use.")
    
    receive_parser = subparsers.add_parser("receive", help="Receive a file or directory.")
    receive_parser.add_argument("ticket", type=BlobTicket.from_str, help="The ticket to use to connect to the sender.")
    receive_parser.add_argument("--magic-ipv4-addr", type=str, help="IPv4 address to bind to.")
    receive_parser.add_argument("--magic-ipv6-addr", type=str, help="IPv6 address to bind to.")
    receive_parser.add_argument("--format", default="hex", choices=["hex", "cid"], help="Format to display hashes.")
    receive_parser.add_argument("--verbose", action="count", default=0, help="Increase verbosity.")
    receive_parser.add_argument("--relay", default="default", choices=["disabled", "default", "custom"], help="Relay mode to use.")
    
    args = parser.parse_args()
    if args.command == "send":
        await send(args)
    elif args.command == "receive":
        await receive(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())