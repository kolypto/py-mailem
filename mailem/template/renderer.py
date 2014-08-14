from string import Template


class IRenderer(object):
    """ Base class for template renderer """

    def __init__(self, template):
        """ Init renderer with a template string

        :param template: Template string
        :type template: basestring
        """
        raise NotImplementedError()

    def __call__(self, values):
        """ Render a template with the provided values.

        :param values: Values to render the template with.
        :type values: dict
        :returns: Rendered template
        :rtype: basestring
        """
        raise NotImplementedError()


class PythonTemplateRenderer(IRenderer):
    """ Simple Python Template renderer.

        Supported substitutions:

        * PythonTemplateRenderer('$what')(what=1)  #-> '1'
        * PythonTemplateRenderer('${what}')(what=1)  #-> '1'
        * PythonTemplateRenderer('$$what')(what=1)  #-> '$what'
    """

    def __init__(self, template):
        self.template = Template(template)

    def __call__(self, values):
        return self.template.substitute(values)
