from prefect import task,flow


@task(log_prints=True)
def print_capture(txt):
    print("This is within print_capture.")
    # print(f"user input: {txt}")

@flow(log_prints=True)
def main_pfunc(txt):
    print("main function call initiated")
    print_capture(txt)

# if __name__=="__main__":
#     main.serve(name="prefect-test-run-v2")