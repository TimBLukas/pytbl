import unittest
from unittest.mock import Mock, patch

import ui
from ui import buttons, container, style, widgets


class FakeBooleanVar:
    def __init__(self, master=None, value=False):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class UIFacadeTests(unittest.TestCase):
    def test_facade_exports_common_symbols(self):
        self.assertTrue(callable(ui.create_button))
        self.assertTrue(callable(ui.create_sidebar))
        self.assertTrue(callable(ui.create_header))
        self.assertTrue(callable(ui.create_circle_button))


class UIStyleTests(unittest.TestCase):
    def test_style_helpers_use_root_and_expected_names(self):
        fake_style = Mock()
        fake_style.configure = Mock()
        fake_style.map = Mock()

        with patch("ui.style.ttk.Style", return_value=fake_style) as style_cls:
            self.assertEqual(style.get_entry_style("root", error=True), "Error.TEntry")
            self.assertEqual(style.get_alert_style("root", "warning"), "Warning.Alert.TFrame")
            self.assertEqual(style.get_sidebar_style("root", active=True), "Active.Sidebar.TButton")

        self.assertEqual(style_cls.call_args_list[0].args[0], "root")
        self.assertEqual(style_cls.call_args_list[1].args[0], "root")
        self.assertEqual(style_cls.call_args_list[2].args[0], "root")

        fake_style.configure.assert_any_call(
            "Error.TEntry",
            fieldbackground="#ffffff",
            bordercolor="#e03131",
            lightcolor="#e03131",
            darkcolor="#e03131",
            padding=8,
        )
        fake_style.configure.assert_any_call(
            "Warning.Alert.TFrame", background="#f08c00", relief="flat"
        )
        fake_style.configure.assert_any_call(
            "Active.Sidebar.TButton",
            font=("Segoe UI", 10, "bold"),
            background="#e9ecef",
            foreground="#1c7ed6",
            anchor="w",
            padding=(20, 10),
            borderwidth=0,
        )

    def test_invalid_style_variants_raise(self):
        with self.assertRaises(ValueError):
            style.get_label_style("root", "bad")
        with self.assertRaises(ValueError):
            style.get_progress_style("root", "bad")
        with self.assertRaises(ValueError):
            style.get_alert_style("root", "bad")
        with self.assertRaises(ValueError):
            style.get_tag_style("root", "bad")


class UIButtonTests(unittest.TestCase):
    def test_create_button_applies_variant_style_and_dimensions(self):
        button_mock = Mock()
        with patch.dict(
            buttons._VARIANT_STYLE_GETTERS,
            {buttons.ButtonVariant.SUCCESS: lambda parent: "Success.TButton"},
            clear=False,
        ), patch("ui.buttons.ttk.Button", return_value=button_mock) as button_cls:
            command = Mock()
            result = buttons.create_button(
                "parent",
                "Save",
                command,
                variant=buttons.ButtonVariant.SUCCESS,
                width=12,
                height=20,
                disabled=True,
            )

        self.assertIs(result, button_mock)
        button_cls.assert_called_once_with(
            "parent", text="Save", style="Success.TButton", command=command
        )
        button_mock.configure.assert_any_call(width=12)
        button_mock.configure.assert_any_call(padding=(12, 20))
        button_mock.state.assert_called_once_with(["disabled"])

    def test_toggle_button_flips_state_and_calls_callback(self):
        button_mock = Mock()
        var = FakeBooleanVar(value=False)
        callback = Mock()

        with patch("ui.buttons.tk.BooleanVar", return_value=var), patch(
            "ui.buttons.get_default_btn_style", return_value="Default.TButton"
        ), patch("ui.buttons.ttk.Button", return_value=button_mock) as button_cls:
            toggle = buttons.create_toggle_button(
                "parent", "On", "Off", initial=False, on_toggle=callback
            )

        self.assertIs(toggle.widget, button_mock)
        button_cls.assert_called_once()
        self.assertEqual(button_cls.call_args.kwargs["text"], "Off")
        button_cls.call_args.kwargs["command"]()
        self.assertTrue(toggle.is_on.get())
        button_mock.configure.assert_called_once_with(text="On")
        callback.assert_called_once_with(True)

    def test_create_circle_button_rejects_missing_content(self):
        with self.assertRaises(ValueError):
            buttons.create_circle_button("parent", None, None, lambda: None)


class UIContainerTests(unittest.TestCase):
    def test_factory_validations_raise(self):
        with self.assertRaises(ValueError):
            container.create_sidebar("parent", width=0)
        with self.assertRaises(ValueError):
            container.create_grid_container("parent", columns=0)
        with self.assertRaises(ValueError):
            widgets.create_header("parent", "Title", level=3)
        with self.assertRaises(ValueError):
            widgets.create_progress_bar("parent", mode="bad")
        with self.assertRaises(ValueError):
            widgets.create_dropdown("parent", ["A"], default="B")
        with self.assertRaises(ValueError):
            widgets.create_step_indicator("parent", [], current=0)
        with self.assertRaises(ValueError):
            widgets.create_step_indicator("parent", ["A"], current=1)

    def test_modal_and_collapsible_factories_return_components(self):
        pane = object()
        overlay = object()
        with patch("ui.container.CollapsiblePane", return_value=pane) as pane_cls, patch(
            "ui.container.ModalOverlay", return_value=overlay
        ) as overlay_cls:
            self.assertIs(container.create_collapsible_pane("parent", "Title"), pane)
            self.assertIs(container.create_modal_overlay("root"), overlay)

        pane_cls.assert_called_once_with("parent", "Title", True)
        overlay_cls.assert_called_once_with("root")


if __name__ == "__main__":
    unittest.main()
