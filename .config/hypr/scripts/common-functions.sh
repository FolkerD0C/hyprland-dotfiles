HYPRPAPER_SETTER_PIDFILE="/var/run/user/${UID}/hyprpaper_setter_${HYPRLAND_INSTANCE_SIGNATURE}.pid"

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
