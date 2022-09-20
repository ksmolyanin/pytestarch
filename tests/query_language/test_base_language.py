import pytest

from pytestarch.eval_structure.eval_structure_types import Evaluable
from pytestarch.eval_structure.evaluable_graph import EvaluableGraph
from pytestarch.eval_structure.graph import Graph
from pytestarch.importer.import_types import AbsoluteImport
from pytestarch.query_language.base_language import Rule
from pytestarch.query_language.exceptions import ImproperlyConfigured

MODULE_1 = "Module1"
MODULE_2 = "Module2"
MODULE_3 = "Module3"
MODULE_4 = "Module4"
MODULE_5 = "Module5"
MODULE_6 = "Module6"
SUB_MODULE_OF_1 = "Module1.SubModule1"
SUB_SUB_MODULE_OF_1 = "Module1.SubModule1.SubModule1"


def test_rule_to_str_as_expected() -> None:
    rule = Rule()

    rule.modules_that().are_named(
        "A name"
    ).should().import_modules_that().are_sub_modules_of("Module 1")

    rule_as_str = str(rule)

    assert (
        rule_as_str
        == '"A name" should import modules that are sub modules of "Module 1".'
    )


def test_sub_modules_identification() -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of("A name")

    assert rule.rule_subject.name is None
    assert rule.rule_subject.parent_module == "A name"


def test_module_name_identification() -> None:
    rule = Rule()

    rule.modules_that().are_named("A name")

    assert rule.rule_subject.name == "A name"
    assert rule.rule_subject.parent_module is None


@pytest.fixture(scope="module")
def evaluable1() -> Evaluable:
    all_modules = [
        MODULE_1,
        MODULE_2,
        MODULE_3,
        MODULE_4,
        MODULE_5,
        MODULE_6,
        SUB_MODULE_OF_1,
        SUB_SUB_MODULE_OF_1,
    ]
    imports = [
        AbsoluteImport(MODULE_1, MODULE_2),
        AbsoluteImport(MODULE_2, MODULE_3),
        AbsoluteImport(MODULE_4, MODULE_2),
        AbsoluteImport(MODULE_2, MODULE_4),
        AbsoluteImport(MODULE_3, MODULE_5),
        AbsoluteImport(MODULE_6, MODULE_3),
    ]

    return EvaluableGraph(Graph(all_modules, imports))


def test_partially_configured_rule_raises_error(evaluable1: Evaluable) -> None:
    rule = Rule()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleSubject, a BehaviorSpecification, "
        "a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    x = rule.modules_that()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleSubject, a BehaviorSpecification, "
        "a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    y = x.are_named(MODULE_1)

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a BehaviorSpecification, a "
        "DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    z = y.should()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a DependencySpecification, a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    a = z.import_modules_that()

    with pytest.raises(
        ImproperlyConfigured,
        match="Specify a RuleObject.",
    ):
        rule.assert_applies(evaluable1)

    a.are_named(MODULE_2)

    rule.assert_applies(evaluable1)

    assert True


def assert_rule_applies(rule: Rule, evaluable: Evaluable) -> None:
    rule.assert_applies(evaluable)


def assert_not_rule_does_not_apply(rule: Rule, evaluable: Evaluable) -> None:
    with pytest.raises(AssertionError):
        rule.assert_applies(evaluable)


def test_should_import_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(MODULE_1).should().import_modules_that().are_named(
        MODULE_2
    )

    assert_rule_applies(rule, evaluable1)


def test_should_import_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_import_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_import_submodule_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_import_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_submodule_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        SUB_MODULE_OF_1
    ).should().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should_only().import_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should_only().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should_only().import_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_submodule_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should_only().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().import_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().import_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().import_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_submodule_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().import_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_4
    ).should_not().import_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_4
    ).should_not().import_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should_not().import_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_submodule_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should_not().import_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should_not().import_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should_not().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should_not().import_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_submodule_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should_not().import_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().import_modules_except_modules_that().are_named(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should().import_modules_except_modules_that().are_named(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_rule_applies(rule, evaluable1)


def test_should_import_except_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should().import_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_1
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_import_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_1
    ).should().import_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_except_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().import_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_except_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().import_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_except_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().import_modules_except_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().import_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_only_import_except_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().import_modules_except_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_except_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().import_modules_except_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_except_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().import_modules_except_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_import_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().import_modules_except_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_except_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_not().import_modules_except_modules_that().are_named(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_except_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_not().import_modules_except_modules_that().are_sub_modules_of(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_except_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_not().import_modules_except_modules_that().are_named(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_not().import_modules_except_modules_that().are_sub_modules_of(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_not_import_except_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_not().import_modules_except_modules_that().are_named(MODULE_4)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_except_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_not().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_except_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_not().import_modules_except_modules_that().are_named(MODULE_4)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_import_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_not().import_modules_except_modules_that().are_sub_modules_of(MODULE_4)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should().be_imported_by_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should().be_imported_by_modules_that().are_named(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_submodule_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_2)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should().be_imported_by_modules_that().are_named(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should().be_imported_by_modules_that().are_named(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_submodule_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_only().be_imported_by_modules_that().are_named(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_only().be_imported_by_modules_that().are_sub_modules_of(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_only().be_imported_by_modules_that().are_named(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_only().be_imported_by_modules_that().are_sub_modules_of(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().be_imported_by_modules_that().are_named(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should_only().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().be_imported_by_modules_that().are_named(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should_only().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should_not().be_imported_by_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_named_submodule_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_6
    ).should_not().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_submodule_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should_not().be_imported_by_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_6
    ).should_not().be_imported_by_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_not().be_imported_by_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_named_submodule_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_not().be_imported_by_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_submodule_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_not().be_imported_by_modules_that().are_named(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_not().be_imported_by_modules_that().are_sub_modules_of(MODULE_3)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_named_named_positive(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_2
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_1)

    assert_rule_applies(rule, evaluable1)


def test_should_be_imported_except_named_named_negative(evaluable1: Evaluable) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_be_imported_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_4
    ).should().be_imported_by_modules_except_modules_that().are_sub_modules_of(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_except_named_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_named(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_except_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_5
    )

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_except_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_named(MODULE_5)

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_5
    )

    assert_rule_applies(rule, evaluable1)


def test_should_only_be_imported_except_named_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_except_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_2
    )

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_except_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_named(MODULE_2)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_only_be_imported_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_only().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_2
    )

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_except_named_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_not().be_imported_by_modules_except_modules_that().are_named(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_except_named_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_5
    ).should_not().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_3
    )

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_except_submodule_named_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_not().be_imported_by_modules_except_modules_that().are_named(MODULE_3)

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_except_submodule_submodule_positive(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_5
    ).should_not().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_3
    )

    assert_rule_applies(rule, evaluable1)


def test_should_not_be_imported_except_named_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_not().be_imported_by_modules_except_modules_that().are_named(MODULE_6)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_except_named_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_named(
        MODULE_3
    ).should_not().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_6
    )

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_except_submodule_named_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_not().be_imported_by_modules_except_modules_that().are_named(MODULE_6)

    assert_not_rule_does_not_apply(rule, evaluable1)


def test_should_not_be_imported_except_submodule_submodule_negative(
    evaluable1: Evaluable,
) -> None:
    rule = Rule()

    rule.modules_that().are_sub_modules_of(
        MODULE_3
    ).should_not().be_imported_by_modules_except_modules_that().are_sub_modules_of(
        MODULE_6
    )

    assert_not_rule_does_not_apply(rule, evaluable1)
