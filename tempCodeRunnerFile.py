if (datetime.now() - start_time).total_seconds() > 40:
            global_df.to_csv("int.csv")
            is_program_running=False
            subprocess.run(['python', 'libcalls.py'])