class BaseMask(object):
    """
    Masks are the objects that are responsible for controlling user access
    to particular resources, and their attributes and relationships.

    To control access to the resources themselves, Masks have five methods, corresponding to CRUDL:
    * `can_create` (true by default)
    * `can_view` (true by default)
    * `can_list` (false by default)
    * `can_edit` (false by default)
    * `can_delete` (false by default)

    These can and should be used in your route file / controller to control access to the requested resource(s).

    Should one be allowed access at that level,
    Masks can provide more fine-grained access control at the per-attribute and per-relationship level:
    * `fields_cant_view` (always called after `can_view`)
    * `fields_cant_edit` (always called after `can_edit`)
    * `includes_cant_create` (always called after `can_edit`)
    * `includes_cant_view` (always called after `can_view`)
    * `includes_cant_edit` (always called after `can_edit`)
    * `includes_cant_delete` (always called after `can_edit`)

    By using `SchemaResource` and `SchemaParser`,
    the corresponding Mask for your resource will be used at (de)serialization time
    to appropriately remove fields from the output, or disallow their input.
    `SchemaResource` and `SchemaParser`, however,
    will assume that the CRUDL checks have already been used,
    and will not check whether or not the resource *itself* should be (de)serialized.
    As such, please remember to use the CRUDL control methods in your routes.
    """

    @classmethod
    def can_create(cls, user_id):
        """
        Typically used in routes like `POST /widgets`

        :param user_id: The user on behalf of whom permission is being requested
        :return: A boolean value indicating whether or not the given user
        is allowed to create wholly new instances of this resource
        """
        return True

    @classmethod
    def can_view(cls, model, user_id):
        """
        Typically used in routes like `GET /widgets/12`
        Note: Sometimes the user is allowed to see a limited version of the requested resource.
        If that is the case, this method should return True,
        and `fields_cant_view` and `includes_cant_view` should be used
        to control which attributes and relationships are actually visible

        :param model: The model which the user is trying to view
        :param user_id: The user on behalf of whom permission is being requested
        :return: A boolean value indicating whether or not the given user
        is allowed to view the given resource at all.
        """
        return True

    @classmethod
    def can_list(cls, user_id):
        """
        Typically used in routes like `GET /widgets`

        :param user_id: The user on behalf of whom permission is being requested
        :return: A boolean value indicating whether or not the given user
        is allowed to list all resources of this type.
        """
        return False

    @classmethod
    def can_edit(cls, model, user_id):
        """
        Typically used in routes like `PATCH /widgets/12`
        Note: Sometimes the user is allowed to edit a limited version of the requested resource.
        If that is the case, this method should return True,
        and `fields_can_edit` and `includes_cant_edit` should be used
        to control which attributes and relationships are actually editable.

        :param model: The model which the user is trying to edit
        :param user_id: The user on behalf of whom permission is being requested
        :return: A boolean value indicating whether or not the given user
        is allowed to edit any attributes or relationships of the given resource.
        """
        return False

    @classmethod
    def can_delete(cls, model, user_id):
        """
        Typically used in routes like `DELETE /widgets/12`

        :param model: The model which the user is trying to delete
        :param user_id: The user on behalf of whom permission is being requested
        :return: A boolean value indicating whether or not the given user
        is allowed to delete the given resource.
        """
        return False

    @classmethod
    def fields_cant_view(cls, model, user_id):
        """
        :param model: The model which the user is trying to view attributes of
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which attributes the given user is not allowed to view.
        """
        return []

    @classmethod
    def fields_cant_edit(cls, model, user_id):
        """
        :param model: The model which the user is trying to edit
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which attributes the given user is not allowed to edit.
        """
        return []

    @classmethod
    def includes_cant_create(cls, model, user_id):
        """
        :param model: The model which the user is trying to edit by creating new relationships
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which relationships the given user
        is not allowed to create or add to.
        """
        return []

    @classmethod
    def includes_cant_view(cls, model, user_id):
        """
        :param model: The model which the user is trying to view relationships of
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which relationships the given user is not allowed to view.
        """
        return []

    @classmethod
    def includes_cant_edit(cls, model, user_id):
        """
        :param model: The model which the user is trying to edit
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which relationships the given user is not allowed to edit.
        """
        return []

    @classmethod
    def includes_cant_delete(cls, model, user_id):
        """
        :param model: The model which the user is trying to edit by deleting existing relationships
        :param user_id: The user on behalf of whom permission is being requested
        :return: A list of strings indicating which relationships the given user
        is not allowed to delete or remove from.
        """
        return []
