"""Deal with OpenAPI v3."""
import json
import re

from jinja2 import Environment, FileSystemLoader


class OpenAPI:  # pylint: disable=too-few-public-methods
    """Create OpenAPI skeleton."""

    def __init__(self, napp_path, tpl_path):
        """Instantiate an OpenAPI object.

        Args:
            napp_path (string): Napp directory
            tlp_path (string): File name from template

        """
        self._napp_path = napp_path
        self._template = tpl_path / 'openapi.yml.template'
        self._api_file = napp_path / 'openapi.yml'

        self._napp_dict = self._parse_napp_metadata()

        # Data for a path
        self._summary = None
        self._description = None

        # Part of template context
        self._paths = {}

    def render_template(self):
        """Render and save API doc in openapi.yml."""
        self._parse_paths()
        context = dict(napp=self._napp_dict, paths=self._paths)
        self._save(context)

    def _parse_napp_metadata(self):
        """Return a NApp metadata file."""
        filename = self._napp_path / 'kytos.json'
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
        return data

    def _parse_paths(self):
        main_file = self._napp_path / 'main.py'
        code = main_file.open().read()
        return self._parse_decorated_functions(code)

    def _parse_decorated_functions(self, code):
        """Return URL rule, HTTP methods and docstring."""
        matches = re.finditer(r"""
                # @rest decorators
                (?P<decorators>
                    (?:@rest\(.+?\)\n)+  # one or more @rest decorators inside
                )
                # docstring delimited by 3 double quotes
                .+?"{3}(?P<docstring>.+?)"{3}
                """, code, re.VERBOSE | re.DOTALL)

        for function_match in matches:
            m_dict = function_match.groupdict()
            self._parse_docstring(m_dict['docstring'])
            self._add_function_paths(m_dict['decorators'])

    def _get_absolute_rule(self, rule):
        napp_prefix = "/api/{username}/{name}/"
        relative_rule = rule[1:] if rule.startswith('/') else rule
        return napp_prefix.format_map(self._napp_dict) + relative_rule

    def _add_function_paths(self, decorators_str):
        for rule, parsed_methods in self._parse_decorators(decorators_str):
            absolute_rule = self._get_absolute_rule(rule)
            path_url = self._rule2path(absolute_rule)
            path_methods = self._paths.setdefault(path_url, {})
            self._add_methods(parsed_methods, path_methods)

    def _parse_docstring(self, docstring):
        """Parse the method docstring."""
        match = re.match(r"""
            # Following PEP 257
            \s* (?P<summary>[^\n]+?) \s*   # First line

            (                              # Description and YAML are optional
              (\n \s*){2}                  # Blank line

              # Description (optional)
              (
                (?!-{3,})                     # Don't use YAML as description
                \s* (?P<description>.+?) \s*  # Third line and maybe others
                (?=-{3,})?                    # Stop if "---" is found
              )?

              # YAML spec (optional) **currently not used**
              (
                -{3,}\n                       # "---" begins yaml spec
                (?P<open_api>.+)
              )?
            )?
            $""", docstring, re.VERBOSE | re.DOTALL)

        summary = 'TODO write the summary.'
        description = 'TODO write/remove the description'
        if match:
            m_dict = match.groupdict()
            summary = m_dict['summary']
            if m_dict['description']:
                description = re.sub(r'(\s|\n){2,}', ' ',
                                     m_dict['description'])
        self._summary = summary
        self._description = description

    def _parse_decorators(self, decorators_str):
        matches = re.finditer(r"""
             @rest\(

              ## Endpoint rule
              (?P<quote>['"])  # inside single or double quotes
                  (?P<rule>.+?)
              (?P=quote)

              ## HTTP methods (optional)
              (\s*,\s*
                  methods=(?P<methods>\[.+?\])
              )?

             .*?\)\s*$
            """, decorators_str, re.VERBOSE)

        for match in matches:
            rule = match.group('rule')
            methods = self._parse_methods(match.group('methods'))
            yield rule, methods

    @classmethod
    def _parse_methods(cls, list_string):
        """Return HTTP method list. Use json for security reasons."""
        if list_string is None:
            return ('GET',)
        # json requires double quotes
        json_list = list_string.replace("'", '"')
        return json.loads(json_list)

    def _add_methods(self, methods, path_methods):
        for method in methods:
            path_method = dict(summary=self._summary,
                               description=self._description)
            path_methods[method.lower()] = path_method

    @classmethod
    def _rule2path(cls, rule):
        """Convert relative Flask rule to absolute OpenAPI path."""
        typeless = re.sub(r'<\w+?:', '<', rule)  # remove Flask types
        return typeless.replace('<', '{').replace('>', '}')  # <> -> {}

    def _read_napp_info(self):
        filename = self._napp_path / 'kytos.json'
        return json.load(filename.open())

    def _save(self, context):
        tpl_env = Environment(
            loader=FileSystemLoader(str(self._template.parent)),
            trim_blocks=True)
        content = tpl_env.get_template(
            'openapi.yml.template').render(context)
        with self._api_file.open('w') as openapi:
            openapi.write(content)
