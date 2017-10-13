import ctypes
import os
import signal

from .defs import *  # noqa

from . import defs
from ._ptrace import ptrace as _ptrace


def traceme():
    return _ptrace(defs.PTRACE_TRACEME, 0, 0, 0)


def peektext(pid, addr):
    return _ptrace(defs.PTRACE_PEEKTEXT, pid, addr, 0)


def peekdata(pid, addr):
    return _ptrace(defs.PTRACE_PEEKDATA, pid, addr, 0)


def peekuser(pid, addr):
    return _ptrace(defs.PTRACE_PEEKUSER, pid, addr, 0)


def poketext(pid, addr, data):
    return _ptrace(defs.PTRACE_POKETEXT, pid, addr, data)


def pokedata(pid, addr, data):
    return _ptrace(defs.PTRACE_POKEDATA, pid, addr, data)


def pokeuser(pid, addr, data):
    return _ptrace(defs.PTRACE_POKEUSER, pid, addr, data)


def getregs(pid):
    regs = defs.user_regs_struct()
    _ptrace(defs.PTRACE_GETREGS, pid, 0, ctypes.addressof(regs))
    return regs


def getfpregs(pid):
    regs = defs.user_fpregs_struct()
    _ptrace(defs.PTRACE_GETREGS, pid, 0, ctypes.addressof(regs))
    return regs


def getsiginfo(pid):
    siginfo = defs.siginfo_t
    _ptrace(defs.PTRACE_GETSIGINFO, pid, 0, ctypes.addressof(siginfo))
    return siginfo


def setoptions(pid, options):
    return _ptrace(defs.PTRACE_SETOPTIONS, pid, 0, options)


def geteventmsg(pid):
    data = ctypes.c_ulong()
    _ptrace(defs.PTRACE_GETEVENTMSG, pid, 0, ctypes.addressof(data))
    return data.value


def cont(pid, signum=0):
    return _ptrace(defs.PTRACE_CONT, pid, 0, signum)


def syscall(pid, signum=0):
    return _ptrace(defs.PTRACE_SYSCALL, pid, 0, signum)


def kill(pid):
    return _ptrace(defs.PTRACE_KILL, pid, 0, 0)


def attach(pid):
    return _ptrace(defs.PTRACE_ATTACH, pid, 0, 0)


def attach_and_wait(pid, options=0):
    attach(pid)
    wait_for_trace_stop(pid)
    options |= defs.PTRACE_O_TRACESYSGOOD
    setoptions(pid, options)


def wait_for_trace_stop(pid):
    pid, status = wait(pid)

    if os.WIFEXITED(status):
        raise OSError('traced process {} has exited with exit code {}'.format(
            pid, os.WEXITSTATUS(status)))

    elif os.WIFSIGNALED(status):
        raise OSError('traced process {} has been killed by '
                      'the {} signal {}'.format(pid, os.WTERMSIG(status)))

    if not os.WIFSTOPPED(status):
        raise OSError('waitpid({}) returned an unexpected status {}'.format(
            pid, hex(status)))

    stopsig = os.WSTOPSIG(status)
    if stopsig != signal.SIGSTOP:
        raise OSError('waitpid({}) returned an unexpected status {}'.format(
            pid, hex(status)))


def wait(pid, options=0):
    options |= defs.WALL
    return os.waitpid(pid, options)


def detach(pid, signum=0):
    return _ptrace(defs.PTRACE_DETACH, pid, 0, signum)


def is_stop_signal(signum):
    return signum in (signal.SIGSTOP, signal.SIGTSTP,
                      signal.SIGTTIN, signal.SIGTTOU)