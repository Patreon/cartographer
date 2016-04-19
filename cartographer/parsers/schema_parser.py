from cartographer.parsers.jsonapi_parser import PostedDocument
from cartographer.field_types import ArrayRelationship
from cartographer.utils.version import get_default_version


class SchemaParser(PostedDocument):
    """
    SchemaParser turns JSON API inputs into python dictionaries
    suitable to pass as arguments to SQLAlchemy `.insert()` and `.update()` calls
    (hereafter referred to as "table data").
    It does so by subclassing `PostedDocument` and using those convenience methods
    to provide validation and deserialization.
    """

    def __init__(self, json_data=None,
                 inbound_request=None, inbound_session=None,
                 parent_parser=None, relationship_name=None,
                 current_user_id=None,
                 version=None):
        """
        Route files should pass in `inbound_request` and `inbound_session`,
        Resource files should pass in `parent_parser` and `relationship_name`

        :param json_data: The json document which will be parsed into table data
        :param inbound_request: The current `JSONAPIRequest` which is prompting the parsing of this resource
        :param inbound_session: The `JSONAPISession` which is active during the parsing of this resource
        :param parent_parser: The `PostedDocument` which is creating this instance for assistance in parsing one of its related resources
        :param relationship_name: The name by which the parent_parser refers to this instance
        :param current_user_id: The ID of the user on behalf of whom the resource is being parsed
        :param version: The version of the JSON API spec that the posted document is using

        :return: A instance of SchemaParser (or more typically a subclass),
        which will typically have `validated_table_data` called on it in a route
        to extract usable data for our python models.
        """

        if version is None:
            if inbound_request:
                version = inbound_request.get_json_api_version()
            else:
                version = get_default_version()
        if json_data is None and inbound_request:
            json_data = inbound_request.get_json(force=True)
        super().__init__(json_data=json_data, version=version)

        if parent_parser and not current_user_id:
            current_user_id = parent_parser.current_user_id

        if current_user_id is None and inbound_session:
            current_user_id = inbound_session.user_id
        self.current_user_id = str(current_user_id)

        self._table_data = None

    @classmethod
    def schema(cls):
        """Override this in a subclass to define model <=> API mappings"""
        raise NotImplementedError()

    def validated_table_data(self):
        """The primary use case for this class. Simply calls validate, then returns the table data"""
        self.validate(self.data())
        return self.table_data()

    # # Parsing

    def table_data(self):
        """
        The primary entry point for parsing.

        :return: A map from column names to their values
        """
        if self._table_data is None:
            result = {}

            data = self.data()

            json_attributes = data.json_data.get('attributes', {})
            if json_attributes:
                for key in json_attributes:
                    if self.should_parse_attribute(key):
                        parsed_attribute = self.parse_schema_attribute(key)
                        if parsed_attribute and len(parsed_attribute) == 2:
                            result_key, parsed_value = parsed_attribute
                            result[result_key] = parsed_value

            json_relationships = data.json_data.get('relationships', {})
            if json_relationships:
                for key in json_relationships:
                    if self.should_parse_relationship(key):
                        parsed_relationship = self.parse_schema_relationship(key)
                        if parsed_relationship and len(parsed_relationship) == 2:
                            result_key, parsed_value = parsed_relationship
                            result[result_key] = parsed_value

            self._table_data = result
        return self._table_data

    # Attributes

    def parse_schema_attribute(self, key):
        """
        Note: currently only handles SchemaAttributes which are model properties.
        The assumption here is that computed values are read-only.

        :param key: The name of the attribute to be parsed
        :return: A tuple of the model property name and its corresponding parsed value
        """
        schema_attribute = self.schema().attribute(key)
        if schema_attribute \
                and schema_attribute.model_attribute \
                and schema_attribute.is_property:
            serialized_value = self.data().attribute(key)
            return schema_attribute.model_attribute, schema_attribute.from_json(serialized_value)
        # TODO: let SchemaAttribute declare parser_method

    def should_parse_attribute(self, key):
        return key in self.schema().attributes()

    # Relationships

    def parse_schema_relationship(self, key):
        """
        Note: currently only handles SchemaRelationships which are map to foreign keys.
        This is because rich objects are not `insert`-able or `update`-able,
        and the return format is column values.

        :param key: The name of the relationship to be parsed
        :return: A tuple of the model property name and its corresponding parsed value.
        Note: for to-many relationships, the return value is formatted as a tuple with
        * the relationship key
        * an array of maps from 'id' *for the other table* to corresponding parsed values.
        """
        schema_relationship = self.schema().relationship(key)
        if schema_relationship:
            # TODO: redo array relationship parsing.
            # there was a thing where everything was nested under keys. probably that.
            if isinstance(schema_relationship, ArrayRelationship):
                return key, [
                    {'id': x.resource_id()}
                    for x in self.data().relationship_id(key)
                ]
            elif schema_relationship.id_attribute:
                return schema_relationship.id_attribute, self.data().relationship_id(key).resource_id()
        return None
        # TODO: let SchemaRelationship declare parser_method

    def should_parse_relationship(self, key):
        return key in self.schema().relationships()

    # # Validation

    def validate(self, inbound_data):
        """Override this in a subclass to enforce format and content rules for the inbound JSON API document"""
        pass
