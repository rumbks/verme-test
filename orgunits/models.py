"""
Copyright 2020 ООО «Верме»
"""
from django.db import models


class OrganizationQuerySet(models.QuerySet):
    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """
        # children = self.raw(f"""
        # WITH RECURSIVE children as (
        #     SELECT id, name, code, parent_id
        #     FROM orgunits_organization
        #     WHERE id={root_org_id}
        #
        #     UNION
        #
        #     SELECT orgunits_organization.id, orgunits_organization.name, orgunits_organization.code, orgunits_organization.parent_id
        #        FROM orgunits_organization
        #           JOIN children
        #               ON orgunits_organization.parent_id = children.id
        # )
        # SELECT * FROM children;""")
        children = self.all().extra(where=[f"""
        orgunits_organization.id IN 
            
            (WITH RECURSIVE children as (
                SELECT id
                FROM orgunits_organization
                WHERE id={root_org_id}

                UNION

                SELECT orgunits_organization.id
                   FROM orgunits_organization
                      JOIN children
                          ON orgunits_organization.parent_id = children.id
            )
            SELECT * FROM children)"""])
        return children


    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """

        # parents = self.raw(f"""
        # WITH RECURSIVE parents as (
        #     SELECT id, name, code, parent_id
        #     FROM orgunits_organization
        #     WHERE id={child_org_id}
        #
        #     UNION
        #
        #     SELECT orgunits_organization.id, orgunits_organization.name, orgunits_organization.code, orgunits_organization.parent_id
        #        FROM orgunits_organization
        #           JOIN parents
        #               ON orgunits_organization.id = parents.parent_id
        # )
        # SELECT * FROM parents;""")
        parents = self.all().extra(
                where=[f"""
        orgunits_organization.id IN 
            (WITH RECURSIVE parents as (
                SELECT id, parent_id
                FROM orgunits_organization
                WHERE id={child_org_id}

                UNION

                SELECT orgunits_organization.id, orgunits_organization.parent_id
                   FROM orgunits_organization
                      JOIN parents
                          ON orgunits_organization.id = parents.parent_id
            )
            SELECT id FROM parents)"""])

        return parents


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организация"
        verbose_name = "Организации"

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """
        upwards = Organization.objects.tree_upwards(self.id)
        return upwards.exclude(id=self.id)

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """
        downwards = Organization.objects.tree_downwards(self.id)
        return downwards.exclude(id=self.id)

    def __str__(self):
        return self.name
