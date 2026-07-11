Option Explicit

Dim args, shell, command, index, value, exitCode
Set args = WScript.Arguments

If args.Count < 1 Then WScript.Quit 64

command = ""
For index = 0 To args.Count - 1
    value = CStr(args(index))
    If InStr(value, Chr(34)) > 0 Or InStr(value, vbCr) > 0 Or InStr(value, vbLf) > 0 Then
        WScript.Quit 65
    End If
    If index > 0 Then command = command & " "
    command = command & Chr(34) & value & Chr(34)
Next

Set shell = CreateObject("WScript.Shell")
exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode
