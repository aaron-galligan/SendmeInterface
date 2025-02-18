import subprocess
import sendme_module as sm
import asyncio
import time





async def start_subprocess():
    process = await asyncio.create_subprocess_shell(
        'sendme send requirements.txt',
        stdout=asyncio.subprocess.PIPE
    )
    return process



async def run_subprocess():
    # Start the subprocess
    process = await start_subprocess()

    async def read_output(stream):
        while True:
            line = await stream.readline()
            print(line.decode().rstrip())
            if "sendme receive" in line.decode().rstrip():
                break

    
    print("before readoutput")
    await read_output(process.stdout)
    print("after first readoutput")

    try:
        # Wait for 5 seconds
        await asyncio.sleep(5)

        # Attempt to terminate the subprocess
        print("Terminating the subprocess...")
        process.terminate()  # Graceful termination

        # Optionally, wait for the process to terminate
        await process.wait()  # Ensure the process is cleaned up
        print("Subprocess terminated.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the asynchronous function
asyncio.run(run_subprocess())