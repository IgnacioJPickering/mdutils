from pathlib import Path


def make_path_relative(base: Path, target: Path) -> Path:
    base_parts = base.parts
    target_parts = target.parts
    for i, (base_part, targ_part) in enumerate(zip(base_parts, target_parts)):
        # When we find the first part that is different, walk
        # backwards with .. and join the rest
        if base_part != targ_part:
            return Path(*(".." for _ in base_parts[i:])) / Path(*target_parts[i:])
    # If target has the full "base" as a prefix, then just return the relative path
    return target.relative_to(base)
