"""
Tests for AST v2.1 Models.

Tests cover:
1. New models: TestCaseIdRule, ExpectedOutput, ExpansionStep, PostAction
2. Enhanced models: ViewpointMapping, DTSubTableRow, ProcedureStep, PreCondition, Message
3. Integration: AstModel v2.1 features
4. Backward compatibility: NavigationStep alias
"""
import pytest
from workflow_client.models.ast import (
    # Main AST
    AstModel,
    ASTv2,
    create_empty_ast,
    # Component 1
    ScreenClassification,
    OutputFileMapping,
    # Component 2
    WidgetRegistry,
    Widget,
    # Component 3
    WidgetViewpointMapping,
    ViewpointMapping,
    TestDataSample,
    # Component 4
    TestScenario,
    NavigationStep,
    ProcedureStep,
    PreCondition,
    TestGroup,
    # Component 5
    DecisionTable,
    DTCondition,
    DTSubTable,
    DTSubTableRow,
    ExpansionStep,
    PostAction,
    # Component 6
    BusinessRules,
    Message,
    # Component 8
    ExpectedTestCount,
    # v2.1 models
    TestCaseIdRule,
    ExpectedOutput,
    MessageRef,
    DisplayFormat,
    # Enums
    ScreenType,
    MessageType,
    ScenarioCategory,
)


class TestTestCaseIdRule:
    """Tests for TestCaseIdRule model (v2.1)."""

    def test_create_with_defaults(self):
        """Test creating rule with default values."""
        rule = TestCaseIdRule(prefix="011")
        assert rule.prefix == "011"
        assert rule.format_pattern == "[{prefix}-{counter:02d}]"
        assert rule.counter_start == 1
        assert rule.section_reset is True

    def test_generate_id(self):
        """Test ID generation."""
        rule = TestCaseIdRule(prefix="011")
        assert rule.generate_id(1) == "[011-01]"
        assert rule.generate_id(2) == "[011-02]"
        assert rule.generate_id(10) == "[011-10]"
        assert rule.generate_id(99) == "[011-99]"

    def test_from_screen_id(self):
        """Test creating rule from screen ID."""
        rule = TestCaseIdRule.from_screen_id("SC-011")
        assert rule.prefix == "011"
        assert rule.generate_id(1) == "[011-01]"

        # Test lowercase
        rule2 = TestCaseIdRule.from_screen_id("sc-005")
        assert rule2.prefix == "005"

    def test_custom_format_pattern(self):
        """Test custom format patterns."""
        rule = TestCaseIdRule(
            prefix="TEST",
            format_pattern="TC-{prefix}-{counter:03d}"
        )
        assert rule.generate_id(1) == "TC-TEST-001"
        assert rule.generate_id(100) == "TC-TEST-100"

    def test_custom_counter_start(self):
        """Test custom counter start value."""
        rule = TestCaseIdRule(prefix="011", counter_start=100)
        assert rule.counter_start == 100


class TestExpectedOutput:
    """Tests for ExpectedOutput composite model (v2.1)."""

    def test_create_empty(self):
        """Test creating empty expected output."""
        output = ExpectedOutput()
        assert output.description is None
        assert output.message_refs == []
        assert output.sql_refs == []
        assert output.display_format is None
        assert output.visual_indicators == []

    def test_from_description(self):
        """Test creating from description."""
        output = ExpectedOutput.from_description("Search thành công")
        assert output.description == "Search thành công"
        assert not output.has_messages()
        assert not output.has_sql_refs()

    def test_from_message(self):
        """Test creating from message reference."""
        output = ExpectedOutput.from_message("MSG-044")
        assert output.has_messages()
        assert output.get_message_ids() == ["MSG-044"]
        assert output.message_refs[0].action == "display"

    def test_with_error_display(self):
        """Test creating error display output."""
        output = ExpectedOutput.with_error_display(
            msg_id="MSG-044",
            color="red",
            position="below_input"
        )
        assert output.has_messages()
        assert output.display_format.color == "red"
        assert output.display_format.position == "below_input"
        assert "border_red" in output.visual_indicators

    def test_with_sql_refs(self):
        """Test expected output with SQL references."""
        output = ExpectedOutput(
            description="Search successful",
            sql_refs=["SQL3", "SQL4"]
        )
        assert output.has_sql_refs()
        assert output.sql_refs == ["SQL3", "SQL4"]

    def test_combined_output(self):
        """Test combined description, message, and SQL."""
        output = ExpectedOutput(
            description="Save thành công",
            message_refs=[MessageRef(msg_id="MSG-025", action="display")],
            sql_refs=["SQL3"],
            display_format=DisplayFormat(color="green", position="dialog")
        )
        assert output.description == "Save thành công"
        assert output.has_messages()
        assert output.has_sql_refs()
        assert output.display_format.color == "green"


class TestMessageRef:
    """Tests for MessageRef model (v2.1)."""

    def test_create_with_defaults(self):
        """Test creating with default action."""
        ref = MessageRef(msg_id="MSG-044")
        assert ref.msg_id == "MSG-044"
        assert ref.action == "display"

    def test_custom_action(self):
        """Test custom action types."""
        ref = MessageRef(msg_id="MSG-025", action="confirm")
        assert ref.action == "confirm"


class TestDisplayFormat:
    """Tests for DisplayFormat model (v2.1)."""

    def test_create_empty(self):
        """Test creating empty display format."""
        fmt = DisplayFormat()
        assert fmt.color is None
        assert fmt.position is None
        assert fmt.style is None

    def test_error_format(self):
        """Test error display format."""
        fmt = DisplayFormat(color="red", position="below_input", style="inline")
        assert fmt.color == "red"
        assert fmt.position == "below_input"
        assert fmt.style == "inline"


class TestExpansionStep:
    """Tests for ExpansionStep model (v2.1)."""

    def test_create_basic(self):
        """Test creating basic expansion step."""
        step = ExpansionStep(
            step_number=1,
            action="Click 保存"
        )
        assert step.step_number == 1
        assert step.action == "Click 保存"
        assert step.action_vi is None
        assert step.expected_output is None

    def test_with_expected_output(self):
        """Test expansion step with expected output."""
        step = ExpansionStep(
            step_number=2,
            action="Click 保存",
            action_vi="Nhấn nút Lưu",
            expected_output={"description": "Save successful"}
        )
        assert step.action_vi == "Nhấn nút Lưu"
        assert step.expected_output["description"] == "Save successful"


class TestPostAction:
    """Tests for PostAction model (v2.1)."""

    def test_create_basic(self):
        """Test creating basic post action."""
        action = PostAction(action="Click [閉じる]")
        assert action.action == "Click [閉じる]"
        assert action.action_vi is None

    def test_with_expected_output(self):
        """Test post action with expected output."""
        action = PostAction(
            action="Click [閉じる]",
            action_vi="Nhấn nút Đóng",
            expected_output={"description": "Popup closed"}
        )
        assert action.action_vi == "Nhấn nút Đóng"


class TestDTSubTableRowV21:
    """Tests for DTSubTableRow v2.1 enhancements."""

    def test_default_expansion_factor(self):
        """Test default expansion factor is 1 for backward compatibility."""
        row = DTSubTableRow(
            row_id="DT1-1",
            conditions={"C1": "true"},
            expected_result="Success"
        )
        assert row.expansion_factor == 1
        assert row.expansion_steps == []
        assert row.get_expanded_test_count() == 1

    def test_with_expansion_factor(self):
        """Test row with expansion factor."""
        row = DTSubTableRow(
            row_id="DT1-1",
            conditions={"C1": "true", "C2": "false"},
            expected_result="Table User_Role tạo bản ghi",
            expansion_factor=2,
            expansion_steps=[
                ExpansionStep(step_number=1, action="Select role"),
                ExpansionStep(step_number=2, action="Click 保存")
            ]
        )
        assert row.expansion_factor == 2
        assert len(row.expansion_steps) == 2
        assert row.get_expanded_test_count() == 2


class TestDecisionTableV21:
    """Tests for DecisionTable v2.1 enhancements."""

    def test_empty_post_actions(self):
        """Test decision table with no post actions."""
        dt = DecisionTable(
            dt_id="DT_TEST",
            name="Test DT"
        )
        assert dt.post_actions == []

    def test_with_post_actions(self):
        """Test decision table with post actions."""
        dt = DecisionTable(
            dt_id="DT_SC011_Add",
            name="Add Account DT",
            post_actions=[
                PostAction(action="Click [閉じる]"),
                PostAction(action="Verify result")
            ]
        )
        assert len(dt.post_actions) == 2

    def test_expanded_test_count(self):
        """Test get_total_expanded_test_count method."""
        dt = DecisionTable(
            dt_id="DT_TEST",
            name="Test DT",
            sub_tables=[
                DTSubTable(
                    sub_table_id="DT1",
                    name="DT1",
                    rows=[
                        DTSubTableRow(
                            row_id="DT1-1",
                            conditions={"C1": "true"},
                            expected_result="Result 1",
                            expansion_factor=2
                        ),
                        DTSubTableRow(
                            row_id="DT1-2",
                            conditions={"C1": "false"},
                            expected_result="Result 2",
                            expansion_factor=2
                        )
                    ]
                )
            ]
        )
        # v2.0 behavior: counts rows = 2
        assert dt.get_total_combinations() == 2
        # v2.1 behavior: accounts for expansion = 4
        assert dt.get_total_expanded_test_count() == 4


class TestViewpointMappingV21:
    """Tests for ViewpointMapping v2.1 enhancements."""

    def test_default_v21_fields(self):
        """Test default values for v2.1 fields."""
        vp = ViewpointMapping(
            viewpoint_id="VP-001",
            viewpoint_name="Email validation"
        )
        assert vp.viewpoint_category is None
        assert vp.recommend_items == []

    def test_with_category_and_items(self):
        """Test viewpoint with category and recommend items."""
        vp = ViewpointMapping(
            viewpoint_id="VP-011-008",
            viewpoint_name="Email without @",
            viewpoint_category="Email",
            recommend_items=[
                "- Không chứa @",
                "- Thiếu username",
                "- Thiếu tên miền"
            ]
        )
        assert vp.viewpoint_category == "Email"
        assert len(vp.recommend_items) == 3
        assert "- Không chứa @" in vp.recommend_items


class TestWidgetViewpointMappingV21:
    """Tests for WidgetViewpointMapping v2.1 methods."""

    def test_get_viewpoints_by_category(self):
        """Test filtering viewpoints by category."""
        mapping = WidgetViewpointMapping(
            widget_id="WGT-11",
            widget_name="Email Input",
            viewpoints=[
                ViewpointMapping(
                    viewpoint_id="VP-001",
                    viewpoint_name="Empty check",
                    viewpoint_category="Must"
                ),
                ViewpointMapping(
                    viewpoint_id="VP-002",
                    viewpoint_name="Email without @",
                    viewpoint_category="Email"
                ),
                ViewpointMapping(
                    viewpoint_id="VP-003",
                    viewpoint_name="Email without domain",
                    viewpoint_category="Email"
                )
            ]
        )
        email_vps = mapping.get_viewpoints_by_category("Email")
        assert len(email_vps) == 2

        must_vps = mapping.get_viewpoints_by_category("Must")
        assert len(must_vps) == 1

    def test_get_categories(self):
        """Test getting unique categories."""
        mapping = WidgetViewpointMapping(
            widget_id="WGT-11",
            widget_name="Email Input",
            viewpoints=[
                ViewpointMapping(viewpoint_id="VP-001", viewpoint_name="VP1", viewpoint_category="Must"),
                ViewpointMapping(viewpoint_id="VP-002", viewpoint_name="VP2", viewpoint_category="Email"),
                ViewpointMapping(viewpoint_id="VP-003", viewpoint_name="VP3", viewpoint_category="Email"),
            ]
        )
        categories = mapping.get_categories()
        assert set(categories) == {"Must", "Email"}


class TestTestDataSampleV21:
    """Tests for TestDataSample v2.1 enhancements."""

    def test_with_sql_refs(self):
        """Test test data sample with SQL references."""
        sample = TestDataSample(
            value="test@example.com",
            description="Valid email",
            sql_refs=["SQL3", "SQL4"]
        )
        assert sample.sql_refs == ["SQL3", "SQL4"]

    def test_default_sql_refs(self):
        """Test default empty SQL refs."""
        sample = TestDataSample(value="test")
        assert sample.sql_refs == []


class TestProcedureStepV21:
    """Tests for ProcedureStep v2.1 (enhanced NavigationStep)."""

    def test_backward_compatibility_alias(self):
        """Test NavigationStep is alias for ProcedureStep."""
        assert NavigationStep is ProcedureStep

    def test_basic_step(self):
        """Test creating basic procedure step."""
        step = ProcedureStep(
            step_number=1,
            action="Click textbox"
        )
        assert step.step_number == 1
        assert step.action == "Click textbox"
        assert step.sub_steps == []
        assert step.expected_intermediate is None
        assert step.target_widget is None
        assert step.data_column_ref is None

    def test_with_v21_fields(self):
        """Test procedure step with v2.1 fields."""
        step = ProcedureStep(
            step_number=4,
            action="Check kết quả search",
            action_vi="Kiểm tra kết quả tìm kiếm",
            target_widget="WGT-12",
            sub_steps=[
                "Verify name is populated",
                "Verify organization is populated"
            ],
            expected_intermediate="Search results displayed",
            data_column_ref="D"
        )
        assert len(step.sub_steps) == 2
        assert step.expected_intermediate == "Search results displayed"
        assert step.target_widget == "WGT-12"
        assert step.data_column_ref == "D"


class TestPreConditionV21:
    """Tests for PreCondition v2.1 enhancements."""

    def test_default_v21_fields(self):
        """Test default values for v2.1 fields."""
        pc = PreCondition(
            condition_id="PC-001",
            description="User logged in"
        )
        assert pc.role_requirement is None
        assert pc.system_state is None
        assert pc.data_setup is None
        assert pc.applies_to_dt is None

    def test_with_v21_fields(self):
        """Test pre-condition with v2.1 fields."""
        pc = PreCondition(
            condition_id="PC-001",
            description="user login có role「システム管理者」(System admin)",
            description_vi="Người dùng đăng nhập với vai trò System Admin",
            role_requirement="SystemAdmin",
            system_state="popup_open",
            data_setup="user_not_exists",
            applies_to_dt="DT1"
        )
        assert pc.role_requirement == "SystemAdmin"
        assert pc.system_state == "popup_open"
        assert pc.data_setup == "user_not_exists"
        assert pc.applies_to_dt == "DT1"


class TestMessageV21:
    """Tests for Message v2.1 enhancements."""

    def test_default_v21_fields(self):
        """Test default values for v2.1 fields."""
        msg = Message(
            message_id="MSG-044",
            message_type=MessageType.ERROR,
            message_text="入力形式が正しくありません。"
        )
        assert msg.display_color is None
        assert msg.display_position is None

    def test_with_v21_fields(self):
        """Test message with v2.1 fields."""
        msg = Message(
            message_id="MSG-044",
            message_type=MessageType.ERROR,
            message_text="入力形式が正しくありません。",
            message_text_vi="Định dạng nhập không hợp lệ.",
            display_color="red",
            display_position="below_input"
        )
        assert msg.display_color == "red"
        assert msg.display_position == "below_input"


class TestScreenClassificationV21:
    """Tests for ScreenClassification v2.1 enhancements."""

    def test_without_test_case_id_rule(self):
        """Test screen classification without ID rule."""
        sc = ScreenClassification(
            screen_id="SC-011",
            screen_name="アカウント管理画面",
            screen_type=ScreenType.FORM
        )
        assert sc.test_case_id_rule is None

    def test_with_test_case_id_rule(self):
        """Test screen classification with ID rule."""
        sc = ScreenClassification(
            screen_id="SC-011",
            screen_name="アカウント管理画面",
            screen_type=ScreenType.FORM,
            test_case_id_rule=TestCaseIdRule.from_screen_id("SC-011")
        )
        assert sc.test_case_id_rule is not None
        assert sc.test_case_id_rule.prefix == "011"


class TestAstModelV21:
    """Tests for AstModel v2.1 features."""

    def test_default_version(self):
        """Test default version is 2.1."""
        ast = create_empty_ast("PLAN-001", "SC-011", "Test Screen")
        assert ast.version == "2.1"

    def test_astv2_alias(self):
        """Test ASTv2 is alias for AstModel."""
        assert ASTv2 is AstModel

    def test_get_test_case_id_rule(self):
        """Test get_test_case_id_rule method."""
        ast = create_empty_ast("PLAN-001", "SC-011", "Test Screen")
        assert ast.get_test_case_id_rule() is None

        # Add rule
        ast.screen_classification.test_case_id_rule = TestCaseIdRule.from_screen_id("SC-011")
        rule = ast.get_test_case_id_rule()
        assert rule is not None
        assert rule.prefix == "011"

    def test_generate_test_case_id(self):
        """Test generate_test_case_id method."""
        ast = create_empty_ast("PLAN-001", "SC-011", "Test Screen")

        # Without rule
        assert ast.generate_test_case_id(1) is None

        # With rule
        ast.screen_classification.test_case_id_rule = TestCaseIdRule.from_screen_id("SC-011")
        assert ast.generate_test_case_id(1) == "[011-01]"
        assert ast.generate_test_case_id(5) == "[011-05]"

    def test_get_total_dt_expanded_count(self):
        """Test get_total_dt_expanded_count method."""
        ast = create_empty_ast("PLAN-001", "SC-011", "Test Screen")

        # Add decision table with expansion
        dt = DecisionTable(
            dt_id="DT_TEST",
            name="Test DT",
            sub_tables=[
                DTSubTable(
                    sub_table_id="DT1",
                    name="DT1",
                    rows=[
                        DTSubTableRow(
                            row_id="DT1-1",
                            conditions={"C1": "true"},
                            expected_result="Result",
                            expansion_factor=2
                        ),
                        DTSubTableRow(
                            row_id="DT1-2",
                            conditions={"C1": "false"},
                            expected_result="Result",
                            expansion_factor=2
                        )
                    ]
                )
            ]
        )
        ast.decision_tables.append(dt)

        assert ast.get_total_dt_combinations() == 2
        assert ast.get_total_dt_expanded_count() == 4

    def test_get_summary_v21(self):
        """Test get_summary includes v2.1 fields."""
        ast = create_empty_ast("PLAN-001", "SC-011", "Test Screen")
        ast.screen_classification.test_case_id_rule = TestCaseIdRule.from_screen_id("SC-011")

        # Add DT with expansion
        dt = DecisionTable(
            dt_id="DT_TEST",
            name="Test DT",
            sub_tables=[
                DTSubTable(
                    sub_table_id="DT1",
                    name="DT1",
                    rows=[
                        DTSubTableRow(
                            row_id="DT1-1",
                            conditions={},
                            expected_result="Result",
                            expansion_factor=2
                        )
                    ]
                )
            ]
        )
        ast.decision_tables.append(dt)

        summary = ast.get_summary()
        assert summary["version"] == "2.1"
        assert summary["has_test_case_id_rule"] is True
        assert summary["dt_combinations"] == 1
        assert summary["dt_expanded_test_count"] == 2


class TestBackwardCompatibility:
    """Tests for backward compatibility with v2.0."""

    def test_v20_ast_still_valid(self):
        """Test that v2.0 style AST creation still works."""
        # Create AST without any v2.1 fields
        ast = AstModel(
            plan_id="PLAN-001",
            screen_classification=ScreenClassification(
                screen_id="SC-011",
                screen_name="Test Screen",
                screen_type=ScreenType.FORM
            ),
            widget_registry=WidgetRegistry(),
            expected_testcase_count=ExpectedTestCount(total=50)
        )

        # v2.1 fields should have defaults
        assert ast.screen_classification.test_case_id_rule is None
        assert ast.get_test_case_id_rule() is None

    def test_navigation_step_alias(self):
        """Test NavigationStep works as before."""
        step = NavigationStep(
            step_number=1,
            action="Click button",
            target="/path"
        )
        assert step.step_number == 1
        assert step.action == "Click button"
        # v2.1 fields have defaults
        assert step.sub_steps == []

    def test_dt_row_without_expansion(self):
        """Test DT row without expansion fields still works."""
        row = DTSubTableRow(
            row_id="DT1-1",
            conditions={"C1": "true"},
            expected_result="Success"
        )
        # Default expansion factor is 1 (no expansion)
        assert row.get_expanded_test_count() == 1
