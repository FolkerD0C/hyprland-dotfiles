#!/bin/bash

if pkill rofi; then
  exit 0
fi
 
readonly __lock="󰌾 Lock"
readonly __logout="󰍃 Logout"
readonly __shutdown="󰐥 Poweroff"
readonly __reboot="󰑖 Reboot"
readonly __sleep="󰤄 Suspend"
readonly __cancel="󰜺 Cancel"
 
selected_option=$( \
  echo -e "${__lock}\n${__logout}\n${__sleep}\n${__reboot}\n${__shutdown}\n${__cancel}" \
  | rofi -dmenu -i -mesg "Uptime: $(uptime -p | sed -r -e 's/^\s*up\s*(.+)/\1/')" -theme "~/.config/rofi/powermenu.rasi")

case ${selected_option} in
  "${__lock}")
    hyprlock
    ;;
  "${__logout}")
    loginctl terminate-user $(whoami)
    ;;
  "${__sleep}")
    systemctl suspend
    ;;
  "${__reboot}")
    systemctl reboot
    ;;
  "${__shutdown}")
    systemctl poweroff
    ;;
  *)
    ;;
esac
