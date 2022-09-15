import os

import pytest

import gradio as gr
from gradio import processing_utils

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"


class TestExamples:
    def test_handle_single_input(self):
        examples = gr.Examples(["hello", "hi"], gr.Textbox())
        assert examples.processed_examples == [["hello"], ["hi"]]

        examples = gr.Examples([["hello"]], gr.Textbox())
        assert examples.processed_examples == [["hello"]]

        examples = gr.Examples(["test/test_files/bus.png"], gr.Image())

        tmp_filename = examples.processed_examples[0][0]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE

    def test_handle_multiple_inputs(self):
        examples = gr.Examples(
            [["hello", "test/test_files/bus.png"]], [gr.Textbox(), gr.Image()]
        )
        assert examples.processed_examples[0][0] == "hello"
        tmp_filename = examples.processed_examples[0][1]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE

    def test_handle_directory(self):
        examples = gr.Examples("test/test_files/images", gr.Image())

        tmp_filename = examples.processed_examples[0][0]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE

        tmp_filename = examples.processed_examples[1][0]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE

    def test_handle_directory_with_log_file(self):
        examples = gr.Examples(
            "test/test_files/images_log", [gr.Image(label="im"), gr.Text()]
        )

        tmp_filename = examples.processed_examples[0][0]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE
        assert examples.processed_examples[0][1] == "hello"

        tmp_filename = examples.processed_examples[1][0]["name"]
        assert tmp_filename is not None

        encoded = processing_utils.encode_file_to_base64(
            tmp_filename, encryption_key=None
        )
        assert encoded == gr.media_data.BASE64_IMAGE
        assert examples.processed_examples[1][1] == "hi"


class TestExamplesDataset:
    def test_no_headers(self):
        examples = gr.Examples("test/test_files/images_log", [gr.Image(), gr.Text()])
        assert examples.dataset.headers == []

    def test_all_headers(self):
        examples = gr.Examples(
            "test/test_files/images_log",
            [gr.Image(label="im"), gr.Text(label="your text")],
        )
        assert examples.dataset.headers == ["im", "your text"]

    def test_some_headers(self):
        examples = gr.Examples(
            "test/test_files/images_log", [gr.Image(label="im"), gr.Text()]
        )
        assert examples.dataset.headers == ["im", ""]


class TestProcessExamples:
    @pytest.mark.asyncio
    async def test_predict_example(self):
        io = gr.Interface(lambda x: "Hello " + x, "text", "text", examples=[["World"]])
        prediction = await io.examples_handler.predict_example(0)
        assert prediction[0] == "Hello World"

    @pytest.mark.asyncio
    async def test_coroutine_process_example(self):
        async def coroutine(x):
            return "Hello " + x

        io = gr.Interface(coroutine, "text", "text", examples=[["World"]])
        prediction = await io.examples_handler.predict_example(0)
        assert prediction[0] == "Hello World"

    @pytest.mark.asyncio
    async def test_caching(self):
        io = gr.Interface(
            lambda x: "Hello " + x,
            "text",
            "text",
            examples=[["World"], ["Dunya"], ["Monde"]],
        )
        io.launch(prevent_thread_lock=True)
        await io.examples_handler.cache_interface_examples()
        prediction = await io.examples_handler.load_from_cache(1)
        io.close()
        assert prediction[0] == "Hello Dunya"
