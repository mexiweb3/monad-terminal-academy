/*
 * Monad Terminal Academy — override del plugin history default de Evennia.
 *
 * Comportamiento terminal real:
 *   - ArrowUp / ArrowDown (sin Shift) → navega history
 *   - Tab → autocompleta comando si solo hay un token
 *   - Tab después de cd/cat/head/tail/wc/grep + espacio → completa archivos/dirs
 *     del room si el cliente los ha visto (se capturan del output de `ls`).
 */
let history = (function () {

    var historyMax = 100;
    var hist = [""];
    var pos = 0;

    // Comandos conocidos del juego (Academy + core Evennia)
    var COMMANDS = [
        "ls", "dir", "pwd", "cd", "cat", "touch", "mkdir", "grep",
        "echo", "whoami", "head", "tail", "wc", "man", "history",
        "link", "wallet", "quests", "q", "claim",
        "help", "look", "inventory", "inv", "i", "say", "pose",
        "who", "quit", "logout", "create", "connect"
    ];

    // Comandos que reciben archivo/dir como argumento (para TAB en args)
    var FILE_CMDS = ["cd", "cat", "head", "tail", "wc", "grep", "rm"];

    // Contexto del room actual — se llena observando output del servidor.
    var roomContext = {
        exits: [],       // nombres de exits (subdirectorios)
        files: [],       // archivos visibles
    };

    var back = function () {
        pos = Math.min(++pos, hist.length - 1);
        return hist[hist.length - 1 - pos];
    };
    var fwd = function () {
        pos = Math.max(--pos, 0);
        return hist[hist.length - 1 - pos];
    };
    var addHist = function (input) {
        if (input && input !== hist[hist.length - 2]) {
            if (hist.length >= historyMax) hist.shift();
            hist[hist.length - 1] = input;
            hist[hist.length] = "";
        }
    };

    var commonPrefix = function (arr) {
        if (arr.length === 0) return "";
        var p = arr[0];
        for (var i = 1; i < arr.length; i++) {
            while (arr[i].indexOf(p) !== 0) {
                p = p.substring(0, p.length - 1);
                if (p === "") return "";
            }
        }
        return p;
    };

    var completeCommand = function (prefix) {
        var lower = prefix.toLowerCase();
        return COMMANDS.filter(function (c) {
            return c.toLowerCase().indexOf(lower) === 0;
        });
    };

    var completeFileArg = function (prefix) {
        var lower = prefix.toLowerCase();
        var pool = roomContext.exits.concat(roomContext.files);
        return pool.filter(function (name) {
            return name.toLowerCase().indexOf(lower) === 0;
        });
    };

    var doAutocomplete = function (inputfield) {
        var current = inputfield.val() || "";
        var parts = current.split(/\s+/);
        var candidates;
        var lastTokenIndex = current.endsWith(" ") ? parts.length : parts.length - 1;
        var lastToken = current.endsWith(" ") ? "" : parts[parts.length - 1];

        if (lastTokenIndex === 0) {
            // Completando el comando
            candidates = completeCommand(lastToken);
        } else {
            // Completando un argumento (archivo/dir) si el comando es FILE_CMDS
            var cmd = parts[0];
            if (FILE_CMDS.indexOf(cmd) === -1) return; // no completable
            candidates = completeFileArg(lastToken);
        }

        if (candidates.length === 0) return;

        var completion;
        if (candidates.length === 1) {
            completion = candidates[0] + (lastTokenIndex === 0 ? " " : "");
        } else {
            completion = commonPrefix(candidates);
            if (completion.length <= lastToken.length) {
                // No se puede completar más; mostrar lista abajo como bash
                showSuggestions(candidates);
                return;
            }
        }

        // Reconstruir la línea con la nueva completion
        var newParts = parts.slice(0, lastTokenIndex);
        newParts.push(completion);
        inputfield.val(newParts.join(" "));
    };

    var showSuggestions = function (list) {
        // Inyectar las opciones como si fuera output del server (gris)
        var html = '<div style="color:#888; font-family:monospace; white-space:pre-wrap;">' +
                   list.join("  ") + '</div>';
        var $win = $(".main.messagewindow").last();
        if ($win.length === 0) $win = $("#messagewindow");
        if ($win.length === 0) $win = $(".stream").last();
        if ($win.length > 0) {
            $win.append(html);
            $win.scrollTop($win[0].scrollHeight);
        }
    };

    // Captura el contenido del room a partir del output del servidor (inspeccionar ls/look)
    var parseRoomOutput = function (rawText) {
        // Busca líneas tipo "  xxxx/   yyy.txt   zzz/"  y extrae tokens
        if (!rawText) return;
        var lines = rawText.split("\n");
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            // Heurística: líneas con dos+ espacios separando tokens cortos.
            if (/\S\/(\s|$)/.test(line) || /\.\w+(\s|$)/.test(line)) {
                var tokens = line.split(/\s+/).filter(Boolean);
                tokens.forEach(function (t) {
                    if (t.endsWith("/")) {
                        var name = t.slice(0, -1);
                        if (name && roomContext.exits.indexOf(name) === -1) {
                            roomContext.exits.push(name);
                        }
                    } else if (/^[\w\.\-]+$/.test(t)) {
                        if (roomContext.files.indexOf(t) === -1) {
                            roomContext.files.push(t);
                        }
                    }
                });
            }
        }
        // Cap por tamaño
        if (roomContext.exits.length > 50) roomContext.exits = roomContext.exits.slice(-50);
        if (roomContext.files.length > 100) roomContext.files = roomContext.files.slice(-100);
    };

    var resetRoomContextOnCD = function (input) {
        if (/^cd(\s|$)/.test(input) || /^(north|south|east|west|up|down)\b/.test(input)) {
            roomContext.exits = [];
            roomContext.files = [];
        }
    };

    // ===== Plugin hooks =====
    var onKeydown = function (event) {
        var code = event.which;
        var inputfield = $(".inputfield:focus");
        if (inputfield.length < 1) inputfield = $(".inputfield:last");
        if (inputfield.length < 1) inputfield = $("#inputfield");
        if (inputfield.length < 1) return false;

        // Tab — autocompletar
        if (code === 9) {
            event.preventDefault();
            doAutocomplete(inputfield);
            return true;
        }

        // Solo historia si el cursor está al final del texto (como en bash)
        var val = inputfield.val() || "";
        var atEnd = (inputfield[0].selectionStart === val.length);

        // Arrow Up / Down
        if ((code === 38 || code === 40) && atEnd) {
            var startingPos = pos;
            var entry = (code === 38) ? back() : fwd();
            if (entry !== null && entry !== undefined) {
                if (val !== "" && startingPos === 0) addHist(val);
                inputfield.val("");
                inputfield.blur().focus().val(entry);
                event.preventDefault();
                return true;
            }
        }
        return false;
    };

    // Inyecta el comando tipeado en el output area para que quede en el scrollback
    // igual que una terminal real: "$ comando" + output debajo.
    var echoToOutput = function (line) {
        if (!line) return;
        try {
            var $win = $(".main.messagewindow").last();
            if ($win.length === 0) $win = $("#messagewindow");
            if ($win.length === 0) $win = $(".stream").last();
            if ($win.length === 0) return;
            var escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            var html = '<div class="cmd-echo" style="color:#c8f7c5; font-family: ui-monospace, Menlo, Consolas, monospace;">' +
                       '<span style="color:#39ff14; font-weight:700;">$</span> ' +
                       '<span style="color:#ffd166;">' + escaped + '</span>' +
                       '</div>';
            $win.append(html);
            if ($win[0]) $win[0].scrollTop = $win[0].scrollHeight;
        } catch (e) { /* no-op */ }
    };

    var onSend = function (line) {
        addHist(line);
        pos = 0;
        resetRoomContextOnCD(line);
        echoToOutput(line);
        return null;
    };

    // Hook al flujo de texto entrante (para parsear output de ls/look)
    var onText = function (args, kwargs) {
        if (args && args.length > 0) {
            // quitar ANSI
            var clean = (args[0] + "").replace(/\x1b\[[0-9;]*m/g, "");
            parseRoomOutput(clean);
        }
        return null; // no consumir, que siga al siguiente plugin
    };

    return {
        init: function () {},
        onKeydown: onKeydown,
        onSend: onSend,
        onText: onText,
    };
}());
window.plugin_handler.add("history", history);
