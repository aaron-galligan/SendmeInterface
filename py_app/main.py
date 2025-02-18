import iroh
from iroh import Iroh, PublicKey, NodeAddr, AuthorId, Query, SortBy, SortDirection, QueryOptions, path_to_key, key_to_path, NodeOptions
import argparse
import asyncio
import tempfile
import os


async def main():
    # setup event loop, to ensure async callbacks work
    iroh.iroh_ffi.uniffi_set_event_loop(asyncio.get_running_loop())

    # parse arguments
    parser = argparse.ArgumentParser(description='Python Iroh Node Demo')
    parser.add_argument('--ticket', type=str, help='ticket to join a document')

    args = parser.parse_args()

    # create iroh node
    dir = tempfile.TemporaryDirectory()
    options = iroh.NodeOptions()
    options.enable_docs = True
    node = await Iroh.persistent_with_options(dir.name, options)
    node_id = await node.net().node_id()
    print("Started Iroh node: {}".format(node_id))

    if not args.ticket:
        print("In example mode")
        print("(To run the sync demo, please provide a ticket to join a document)")
        print()

        # create doc
        doc = await node.docs().create()
        author = await node.authors().create()
        doc_id = doc.id()
        # create ticket to share doc
        ticket = await doc.share(iroh.ShareMode.READ, iroh.AddrInfoOptions.RELAY_AND_ADDRESSES)

        # add data to doc
        #file_name = input("Enter file name with file extention (file must be in same folder as main): ")
        file_path = "C:/Users/aaron/OneDrive/Documents/Programming/Rust/SendmeInterface/py_app/flag.png"
        file_name = os.path.basename(file_path)
        
        #print(file_name)
        with open(file_path, "rb") as f:
            bytes = bytearray(f.read())
        await doc.set_bytes(author, file_name.encode('utf-8'), bytes)
        print("Created doc: {}".format(doc_id))
        print("Keep this running and in another terminal run:\n\npython main.py --ticket {}".format(ticket))
    else:
        # join doc
        doc_ticket = iroh.DocTicket(args.ticket)
        doc = await node.docs().join(doc_ticket)
        doc_id = doc.id()
        print("Joined doc: {}".format(doc_id))

        # sync & print
        print("Waiting 2 seconds to let stuff sync...")
        await asyncio.sleep(2)

        # query all keys
        query = iroh.Query.all(None)
        keys = await doc.get_many(query)
        #print(keys[0])
        #print(dir(keys[0]))
        print("Data:")
        for entry in keys:
            # get key, hash, and content for each entry
            key = entry.key()
            
            hash = entry.content_hash()
            content = await node.blobs().read_to_bytes(entry.content_hash())
            #print("{}, {} (hash: {})".format(key.decode("utf8"),content.decode("utf8"), hash))
            #copy_path = f"copy_of_{}".format(key.decode("utf8"))
            copy_path = f"copy_of_{key.decode('utf8')}"
            with open(copy_path, "wb") as file:
                file.write(content)


    input("Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())