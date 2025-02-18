import ipfshttpclient
import asyncio

async def send_file(file_path):
    # Connect to IPFS client and add file
    with ipfshttpclient.connect() as client:
        result = client.add(file_path)
        cid = result['Hash']
        print(f"Share this CID with the receiver: {cid}")

async def receive_file(cid, destination_path):
    # Connect to IPFS client and get file by CID
    with ipfshttpclient.connect() as client:
        client.get(cid, target=destination_path)
        print(f"File downloaded to: {destination_path}")

async def main():
    choice = input("Do you want to send (s) or receive (r) a file? ")

    if choice.lower() == 's':
        file_path = input("Enter the path of the file to send: ")
        await send_file(file_path)
    elif choice.lower() == 'r':
        cid = input("Enter the CID provided by the sender: ")
        destination_path = input("Enter the path to save the file: ")
        await receive_file(cid, destination_path)
    else:
        print("Invalid choice. Please enter 's' to send or 'r' to receive.")

if __name__ == "__main__":
    asyncio.run(main())
