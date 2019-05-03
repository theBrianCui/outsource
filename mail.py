from utils import read_file_to_string, get_env, write_string_to_file

SEND_EMAIL_SCRIPT = "scripts/email"
SENDGRID_API_KEY_ENV = "SENDGRID_API_KEY"

def create_email_script(job_name, body_file_path, recipient):
    if not get_env("SENDGRID_API_KEY"):
        raise RuntimeError("SendGrid API key not present in ENV")

    email_script = read_file_to_string(SEND_EMAIL_SCRIPT + ".sh")
    email_script = email_script.replace("SENDGRID_API_KEY", get_env("SENDGRID_API_KEY"))
    email_script = email_script.replace("RECIPIENT", recipient)
    email_script = email_script.replace("SUBJECT", "[outsource] {} job completed".format(job_name))
    email_script = email_script.replace("BODY", "Outsource job {} has been completed and the output log is attached.".format(job_name))
    email_script = email_script.replace("LOG_PATH", body_file_path)

    temp_script_name = SEND_EMAIL_SCRIPT + "_{}.sh.tmp".format(job_name)
    write_string_to_file(email_script, temp_script_name, overwrite=True)
    return temp_script_name
