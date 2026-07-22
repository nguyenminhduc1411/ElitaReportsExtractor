from templates.silk import SilkTemplate
from templates.flap import FlapTemplate


class TemplateEngine:

    def __init__(self):

        self.templates = []

        self.register(SilkTemplate())
        self.register(FlapTemplate())

    def register(self, template):

        self.templates.append(template)

    def parse_page(
        self,
        text,
        config
    ):

        rows = []

        for template in self.templates:

            if not template.match(text):
                continue

            template_config = config.get(template.NAME)

            if template_config is None:
                continue

            result = template.parse(
                text,
                template_config
            )

            rows.extend(result)

        return rows