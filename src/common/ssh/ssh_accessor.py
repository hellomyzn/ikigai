"""common.ssh.ssh_accessor"""
#########################################################
# Builtin packages
#########################################################
import io
from contextlib import contextmanager
from collections.abc import Generator

#########################################################
# 3rd party packages
#########################################################
import paramiko
from paramiko.ed25519key import Ed25519Key
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException

#########################################################
# Own packages
#########################################################
from common.log import (
    error,
    warn,
    debug,
    info
)
from common.exceptions import MyParamikoException


def ssh_exec_command(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    """Execute command in ssh remote

    Usage:
        import os
        host = os.getenv("SSH_HOST", "ssh-stub")
        port = os.getenv("SSH_PORT", "22")
        user = os.getenv("SSH_USER", "root")
        path = os.getenv("SSH_KEY_PATH", "/opt/ssh/id_rsa")
        command = 'docker inspect vpc-gitlab -f "{{json .State.Status}}"'
        with ssh_connect(host, port, user, path) as ssh:
            _, status, _ = ssh_exec_command(ssh, command)

    Args:
        ssh (paramiko.SSHClient): SSH Client
        cmd (str): command to execute

    Raises:
        MyParamikoException: SSH Exception Class

    Returns:
        tuple[int, str, str]: exit code, standard output, standard error output
    """
    try:
        _, stdout, stderr = ssh.exec_command(cmd)
    except Exception as exc:
        mes = f"Failed to execute remote command. Command: {cmd}"
        error(mes)
        raise MyParamikoException(mes) from exc

    exit_code = __retrieve_exit_code(stdout, stderr)

    std_out, std_err = __decode_exec_command_output(stdout, stderr)
    info("Execute the command successfully. command: {0}, exit code: {1}, std_out: {2}, std_err: {3}",
         cmd, exit_code, std_out, std_err)

    return exit_code, std_out, std_err


def __retrieve_exit_code(stdout: paramiko.ChannelFile, stderr: paramiko.ChannelStderrFile) -> int:
    """retrieve exit code

    Args:
        stdout (paramiko.ChannelFile): standard output
        stderr (paramiko.ChannelStderrFile): standard error

    Raises:
        MyParamikoException: SSH Exception Class

    Returns:
        int: exit code
    """
    try:
        exit_code = stdout.channel.recv_exit_status()
    except Exception as exc:
        mes = f"Failed to get command exit status. stdout: {stdout}, stderr: {stderr}"
        error(mes)
        raise MyParamikoException(mes) from exc
    return exit_code


def __decode_exec_command_output(stdout: paramiko.ChannelFile, stderr: paramiko.ChannelStderrFile) -> tuple[str, str]:
    """decode exec command output

    Args:
        stdout (paramiko.ChannelFile): standard output
        stderr (paramiko.ChannelStderrFile): standard error

    Raises:
        MyParamikoException: SSH Exception Class

    Returns:
        tuple[str, str]: standard output text, standard error text
    """
    try:
        std_out = stdout.read().decode("utf-8")
        std_err = stderr.read().decode("utf-8")
    except Exception as exc:
        mes = f"Failed to get command execution result. stdout: {stdout}, stderr: {stderr}"
        error(mes)
        raise MyParamikoException(mes) from exc

    return std_out, std_err


@contextmanager
def ssh_connect(host: str, port: str, user: str, key_path: str) -> Generator[paramiko.SSHClient]:
    """Context manager to connect to ssh remote server

    Args:
        host (str): host
        port (str): port
        user (str): user name
        key_path (str): private key path

    Raises:
        MyParamikoException: SSH Exception Class

    Yields:
        Generator[paramiko.SSHClient]: SSH Client
    """
    if key_path is None:
        raise MyParamikoException(f"key_path is None: {key_path}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    info("SSH connect to: {0}, port: {1}", host, port)
    debug("User: {0}, key_path: {1}", user, key_path)

    pkey_txt = __read_private_key(key_path)

    formatted_private_key = __format_private_key(pkey_txt)
    pkey = __create_pkey_obj(formatted_private_key)

    try:
        try:
            ssh.connect(
                hostname=host,
                port=port,
                username=user,
                pkey=pkey
            )
        except Exception as exc:
            mes = (f"Failed to make SSH connection to host: {host}, "
                   f"port: {port}, user: {user}, key path: {key_path}")
            error(mes)
            raise MyParamikoException(mes) from exc

        info("Success to make SSH connection to host: {0}, port: {1}, user: {2}, key path: {3}",
             host, port, user, key_path)

        yield ssh

    finally:
        ssh.close()


def __read_private_key(key_path: str) -> str:
    """read private key inside

    Args:
        key_path (str): private key path

    Raises:
        MyParamikoException: SSH Exception Class

    Returns:
        str: internal string of private key path
    """
    with open(key_path, encoding="utf-8", mode="r") as f:
        key = f.read()

    if key == "":
        raise MyParamikoException(f"private key is None: {key}")

    debug("read ssh private key: {0}, key")
    return key


def __format_private_key(private_key: str) -> str:
    """format private key

    Args:
        private_key (str): private key

    Returns:
        str: formatted private key
    """

    # consider cases with \n at the end in private key
    private_key = private_key.rstrip()

    # normalize to one line once
    if "\n" in private_key:
        private_key = private_key.replace("\n", " ")

    # for private keys obtained via CICD variables,
    # line breaks are converted to spaces, so replace spaces with new lines.
    splitted_key = private_key.split(" ")
    beg = " ".join(splitted_key[0:4])
    mid = " ".join(splitted_key[4:-4]).replace(" ", "\n")
    end = " ".join(splitted_key[-4:])
    line_break = "\n"

    formatted_key = beg + line_break + mid + line_break + end
    debug("format ssh private key: {0}", formatted_key)
    return formatted_key


def __create_pkey_obj(private_key: str) -> Ed25519Key | RSAKey | None:
    """create pkey object

    Args:
        private_key (str): ssh private key

    Returns:
        Ed25519Key | RSAKey | None: pkey object
    """
    key_types = [
        Ed25519Key,
        RSAKey
    ]
    for key_type in key_types:
        try:
            pkey_str_io = io.StringIO(private_key)
            pkey = key_type.from_private_key(pkey_str_io)
        except SSHException:
            continue
        else:
            debug("pkey object is created. key type: {0}", key_type)
            return pkey
    warn("failed to create pkey object since the key type is incorrect. private key: {0}", private_key)
