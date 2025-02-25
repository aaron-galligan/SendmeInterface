# tests that correspond to the `src/doc.rs` rust api
from iroh import Iroh, PublicKey, NodeAddr, AuthorId, Query, SortBy, SortDirection, QueryOptions, path_to_key, key_to_path, NodeOptions
import tempfile
import os
import asyncio
import iroh

"""
This is code taken from n0-computer/iroh-ffi https://github.com/n0-computer/iroh-ffi/blob/main/python/doc_test.py#L93
and is being used to understand the iroh package
"""

def test_node_addr():
    #
    # create a node_id
    key_str = "ki6htfv2252cj2lhq3hxu4qfcfjtpjnukzonevigudzjpmmruxva"
    node_id = PublicKey.from_string(key_str)
    #
    # create socketaddrs
    ipv4 = "127.0.0.1:3000"
    ipv6 = "::1:3000"
    #
    # relay url
    relay_url = "https://example.com"
    #
    # create a NodeAddr
    expect_addrs = [ipv4, ipv6]
    node_addr = NodeAddr(node_id, relay_url, expect_addrs)
    #
    # test we have returned the expected addresses
    got_addrs = node_addr.direct_addresses()
    for (got, expect) in zip(got_addrs, expect_addrs):
        assert got == expect

    assert relay_url == node_addr.relay_url()

def test_author_id():
    #
    # create id from string
    author_str = "7db06b57aac9b3640961d281239c8f23487ac7f7265da21607c5612d3527a254"
    author = AuthorId.from_string(author_str)
    #
    # call to_string, ensure equal
    assert str(author) == author_str
    #
    # create another id, same string
    author_0 = AuthorId.from_string(author_str)
    #
    # ensure equal
    assert author.equal(author_0)
    assert author_0.equal(author)

def test_query():
    opts = QueryOptions(sort_by=SortBy.KEY_AUTHOR, direction=SortDirection.ASC, offset=10, limit=10)
    # all
    all = Query.all(opts)
    assert 10 == all.offset()
    assert 10 == all.limit()

    # single_latest_per_key
    opts.direction = SortDirection.DESC
    opts.limit = 0
    opts.offset = 0
    single_latest_per_key = Query.single_latest_per_key(opts)
    assert 0 == single_latest_per_key.offset()
    assert single_latest_per_key.limit() is None

    # author
    opts.direction = SortDirection.ASC
    opts.offset = 100
    author = Query.author(AuthorId.from_string("7db06b57aac9b3640961d281239c8f23487ac7f7265da21607c5612d3527a254"), opts)
    assert 100 == author.offset()
    assert author.limit() is None

    # key_exact
    opts.sort_by = SortBy.KEY_AUTHOR
    opts.direction = SortDirection.DESC
    opts.offset = 0
    opts.limit = 100
    key_exact = Query.key_exact(
        b'key',
        opts
    )
    assert 0 == key_exact.offset()
    assert 100 == key_exact.limit()

    # key_prefix
    key_prefix = Query.key_prefix(
        b'prefix',
        opts
    )
    assert 0 == key_prefix.offset()
    assert 100 == key_prefix.limit()


async def test_doc_entry_basics():
    # setup event loop, to ensure async callbacks work
    iroh.iroh_ffi.uniffi_set_event_loop(asyncio.get_running_loop())

    #
    # create node
    dir = tempfile.TemporaryDirectory()
    options = NodeOptions()
    options.enable_docs = True
    node = await Iroh.persistent_with_options(dir.name, options)
    help(node)
    #
    # create doc and author
    doc = await node.docs().create()
    author = await node.authors().create() #author is class AuthorId
    #
    # create entry
    val = b'hello world!'
    key = b'foo'
    hash = await doc.set_bytes(author, key, val)
    #
    # get entry
    query = Query.author_key_exact(author, key)
    entry = await doc.get_one(query)
    assert hash.equal(entry.content_hash())
    assert len(val) == entry.content_len()
    got_val = await node.blobs().read_to_bytes(entry.content_hash())
    assert val == got_val


async def test_doc_import_export():
    # setup event loop, to ensure async callbacks work
    iroh.iroh_ffi.uniffi_set_event_loop(asyncio.get_running_loop())

    #
    # create file temp der
    dir = tempfile.TemporaryDirectory()
    in_root = os.path.join(dir.name, "in")
    out_root = os.path.join(dir.name, "out")
    os.makedirs(in_root, exist_ok=True)
    os.makedirs(out_root, exist_ok=True)
    #
    #
    #testing creating a file inside of temp directory
    
    

    # create file
    temp_path = os.path.join(in_root, "test")
    
    #file_path = os.path.join(dir.name, "requirements.txt")
    with open("requirements.txt", "rb") as f:
        bytes = bytearray(f.read())
    file = open(temp_path, "wb")
    file.write(bytes)
    file.close()
    #

    #await asyncio.sleep(10)
    # create node
    iroh_dir = tempfile.TemporaryDirectory()
    options = NodeOptions()
    options.enable_docs = True
    node = await Iroh.persistent_with_options(iroh_dir.name, options)
    #









    #reveiving computer that has the ticket via email or something
    # create doc and author
    doc = await node.docs().create()
    author = await node.authors().create()
    #
    # import entry
    key = path_to_key(temp_path, None, in_root)
    await doc.import_file(author, key, temp_path, True, None)
    #
    # get entry
    query = Query.author_key_exact(author, key)
    entry = await doc.get_one(query)
    #
    # export entry
    path = key_to_path(key, None, out_root)
    await doc.export_file(entry, path, None)
    #
    # read file
    file = open(path, "rb")
    got_bytes = file.read()
    file.close()
    
    print(bytes == got_bytes)
    #
    #
    assert bytes == got_bytes


async def main():
    await test_doc_import_export()


if __name__ == "__main__":
    asyncio.run(main())