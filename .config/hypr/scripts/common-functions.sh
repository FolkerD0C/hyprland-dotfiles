HYPRPAPER_SETTER_PIDFILE="/tmp/hypr/hyprpaper_setter_${HYPRLAND_INSTANCE_SIGNATURE}.pid"
WAYBAR_SW_NAMED_PIPE="/tmp/hypr/waybar_sw_${HYPRLAND_INSTANCE_SIGNATURE}"
WAYBAR_SW_RUNFILE="/tmp/hypr/waybar-swdn-${HYPRLAND_INSTANCE_SIGNATURE}.runfile"

function debug() {
  [ -n ${HYPRLAND_USERSCRIPTS_DEBUG} ] && echo "[${SCRIPTNAME}]:> {[ ${@} ]}" 1>&2
  if [ -n ${HYPRLAND_USERSCRIPTS_LOGFILE} ]; then
    echo "[$(date '+%Y/%b/%d-%T %Z')][${SCRIPTNAME}]:-:" ${@} >> ${HYPRLAND_USERSCRIPTS_LOGFILE}
  fi
}

function hyprland_is_running() {
  if [ -z "$(hyprctl instances | grep ${HYPRLAND_INSTANCE_SIGNATURE})" ]; then
    echo 'false'
    return
  fi
  echo 'true'
}
