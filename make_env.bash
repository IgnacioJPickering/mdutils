_env_name='amber-utils'

if which mamba > /dev/null; then
    _mamba="mamba"
else
    _mamba="conda"
fi

# Return value of pipe is negated since grep returns 0 on success
! $_mamba env list | awk 'NR>2 {print $1}' | grep -q $_env_name
_env_exists="$?"
if [ $_env_exists -eq 1 ]; then
    _command=update
else
    _command=create
fi

_script_dir="$(dirname "$0")/"
_submodules_dir="${_script_dir}submodules/"
_env_file="${_script_dir}environment.yaml"
$_mamba env "${_command}" -f "${_env_file}"

for d in "${_submodules_dir}"*; do
    _env_file="${d}/environment.yaml"
    _env_file_alt="${d}/environment.yml"
    if [[ -f "${_env_file}" ]]; then
        $_mamba env update --name "${_env_name}" -f "${_env_file}"
    elif [[ -f "${_env_file_short}" ]]; then
        $_mamba env update --name "${_env_name}" -f "${_env_file_short}"
    fi
done
echo "Environment created and updated with submodules"
