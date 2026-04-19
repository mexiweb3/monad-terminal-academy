"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from commands.combat_commands import CmdAttack, CmdFlee, CmdStatus, CmdConsider
from commands.item_commands import CmdUse, CmdEquip, CmdUnequip, CmdInventory, CmdGet, CmdDrop, CmdGive, CmdLoot
from commands.terminal_commands import (
    CmdLS, CmdPWD, CmdCD, CmdCAT, CmdTOUCH, CmdMKDIR, CmdGREP,
    CmdEcho, CmdHead, CmdTail, CmdWC, CmdWhoAmI, CmdMan, CmdClear, CmdHistory,
    CmdClaude,
    CmdNode, CmdNpm, CmdCurl, CmdIrm,
    CmdLink, CmdQuests, CmdClaim,
)
from commands.help_command import CmdHelpCustom
from commands.stats_command import CmdStats


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Combat commands
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdStatus())
        self.add(CmdConsider())
        # Item commands
        self.add(CmdUse())
        self.add(CmdEquip())
        self.add(CmdUnequip())
        self.add(CmdInventory())
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdGive())
        self.add(CmdLoot())
        # Terminal Academy — terminal tutorial + onchain claim
        self.add(CmdLS())
        self.add(CmdPWD())
        self.add(CmdCD())
        self.add(CmdCAT())
        self.add(CmdTOUCH())
        self.add(CmdMKDIR())
        self.add(CmdGREP())
        # Comandos terminal extendidos (Sesión A)
        self.add(CmdEcho())
        self.add(CmdHead())
        self.add(CmdTail())
        self.add(CmdWC())
        self.add(CmdWhoAmI())
        self.add(CmdMan())
        self.add(CmdClear())
        self.add(CmdHistory())
        # Claude CLI — meta-tool de IA
        self.add(CmdClaude())
        # Install Dojo — herramientas CLI reales (Claude Code, OpenClaw, Hermes)
        self.add(CmdNode())
        self.add(CmdNpm())
        self.add(CmdCurl())
        self.add(CmdIrm())
        # Monad onchain
        self.add(CmdLink())
        self.add(CmdQuests())
        self.add(CmdClaim())
        self.add(CmdStats())
        # Onboarding / UX — reemplaza el help default con vista contextual
        self.add(CmdHelpCustom())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
