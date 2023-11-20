from enum import Enum

from ruamel.yaml import YAML, yaml_object

parser = YAML(typ="safe")


class YamlEnum(Enum):
    @classmethod
    def to_yaml(cls, representer, node):  # type: ignore
        return representer.represent_scalar(f"!{cls.__name__}", node.value)

    @classmethod
    def from_yaml(cls, constructor, node):  # type: ignore
        return cls(node.value)


yamlize = yaml_object(parser)
