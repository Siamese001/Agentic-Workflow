# Smart App Control (VerifiedAndReputable) blocks unsigned PyTorch .pyd on Windows.
# Code Integrity event 3077: Policy ID {0283ac0f-fff1-49ae-ada1-8a933130cad6}
param(
    [ValidateSet("Status", "OpenSettings", "DisableDev")]
    [string]$Action = "Status"
)


function Get-SacState {
    $ci = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy" -ErrorAction SilentlyContinue
    $dg = Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard -ErrorAction SilentlyContinue
    [pscustomobject]@{
        VerifiedAndReputablePolicyState = $ci.VerifiedAndReputablePolicyState
        UsermodeCodeIntegrityEnforcement = $dg.UsermodeCodeIntegrityPolicyEnforcementStatus
        CodeIntegrityEnforcement       = $dg.CodeIntegrityPolicyEnforcementStatus
    }
}

switch ($Action) {
    "Status" {
        $s = Get-SacState
        Write-Host "VerifiedAndReputablePolicyState: $($s.VerifiedAndReputablePolicyState) (0=off, 1=on/eval)"
        Write-Host "UsermodeCodeIntegrityEnforcement: $($s.UsermodeCodeIntegrityEnforcement)"
        Write-Host ""
        Write-Host "If apps_rg fails with 'Application Control policy has blocked' on torch/_C.pyd:"
        Write-Host "  A) WSL (no admin): .\tools\apps_rg\Invoke-AppsRgSectionWsl.ps1 --section ..."
        Write-Host "  B) Disable SAC (admin): .\ops_scripts\windows\smart_app_control_apps_rg.ps1 -Action DisableDev"
        Write-Host "  C) UI: Start-Process ms-settings:smart-app-control"
    }
    "OpenSettings" {
        Start-Process "ms-settings:smart-app-control"
    }
    "DisableDev" {
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
            [Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            throw "DisableDev requires elevated PowerShell (Run as Administrator)."
        }
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy" `
            -Name "VerifiedAndReputablePolicyState" -Value 0 -Type DWord
        Write-Host "Set VerifiedAndReputablePolicyState=0. Reboot required."
        Write-Host "Note: Some Windows builds require a clean install to fully remove Smart App Control after it was enabled."
    }
}
