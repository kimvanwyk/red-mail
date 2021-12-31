
from redmail import EmailSender

import re

from pathlib import Path
from io import BytesIO
import pytest
import pandas as pd

import numpy as np

from resources import get_mpl_fig, get_pil_image
from convert import remove_extra_lines


def compare_image_mime(mime_part, mime_part_html, orig_image:bytes):
    assert 'image/png' == mime_part.get_content_type()
    image_bytes = mime_part.get_content()
    assert orig_image == image_bytes

    # Check the HTML mime has the image
    image_info = dict(mime_part.items())
    cid_parts = image_info['Content-ID'][1:-1].split(".")
    cid = "{}.{}.=\n{}.{domain}".format(*cid_parts[:3], domain='.'.join(cid_parts[3:]))
    cid = image_info['Content-ID'][1:-1]

    mime_part_html_cleaned = mime_part_html.get_payload().replace("=\n", "")
    assert f'<img src=3D"cid:{cid}">' in mime_part_html_cleaned or f'<img src="cid:{cid}">' in mime_part_html_cleaned

@pytest.mark.parametrize(
    "get_image_obj", [
        pytest.param(lambda x: str(x), id="Path (str)"),
        pytest.param(lambda x: Path(str(x)), id="Path (pathlib)"),
        pytest.param(lambda x: open(str(x), 'rb').read(), id="Bytes (bytes)"),
        pytest.param(lambda x: BytesIO(open(str(x), 'rb').read()), id="Bytes (BytesIO)"),
        pytest.param(lambda x: {"maintype": "image", "subtype": "png", "content": open(str(x), 'rb').read()}, id="Dict specs"),
    ]
)
def test_with_image_file(get_image_obj, dummy_png):
    with open(str(dummy_png), "rb") as f:
        dummy_bytes = f.read()
    image_obj = get_image_obj(dummy_png)

    sender = EmailSender(server=None, port=1234)
    msg = sender.get_message(
        sender="me@gmail.com",
        receiver="you@gmail.com",
        subject="Some news",
        html_body='<h1>Hi,</h1> Nice to meet you. Look at this shit: <img src="{{ my_image }}">',
        body_images={"my_image": image_obj}
    )
    
    assert "multipart/alternative" == msg.get_content_type()

    #mime_text = msg.get_payload()[0]
    mime_html = msg.get_payload()[0].get_payload()[0]
    mime_image  = msg.get_payload()[0].get_payload()[1]

    compare_image_mime(mime_image, mime_html, orig_image=dummy_bytes)

    # Test receivers etc.
    headers = dict(msg.items())
    assert {
        'from': 'me@gmail.com', 
        'subject': 'Some news', 
        'to': 'you@gmail.com', 
        #'MIME-Version': '1.0', 
        'Content-Type': 'multipart/alternative'
    } == headers

@pytest.mark.parametrize(
    "get_image_obj", [
        pytest.param(get_mpl_fig, id="Matplotlib figure"),
        pytest.param(get_pil_image, id="PIL image"),
    ]
)
def test_with_image_obj(get_image_obj):
    image_obj, image_bytes = get_image_obj()

    sender = EmailSender(server=None, port=1234)
    msg = sender.get_message(
        sender="me@gmail.com",
        receiver="you@gmail.com",
        subject="Some news",
        html_body='<h1>Hi,</h1> Nice to meet you. Look at this shit: <img src="{{ my_image }}">',
        body_images={"my_image": image_obj}
    )
    
    assert "multipart/alternative" == msg.get_content_type()

    #mime_text = msg.get_payload()[0]
    mime_html = msg.get_payload()[0].get_payload()[0]
    mime_image  = msg.get_payload()[0].get_payload()[1]

    compare_image_mime(mime_image, mime_html, orig_image=image_bytes)

    # Test receivers etc.
    headers = dict(msg.items())
    assert {
        'from': 'me@gmail.com', 
        'subject': 'Some news', 
        'to': 'you@gmail.com', 
        #'MIME-Version': '1.0', 
        'Content-Type': 'multipart/alternative'
    } == headers



@pytest.mark.parametrize(
    "df,", [
        pytest.param(
            pd.DataFrame(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                columns=pd.Index(["first", "second", "third"]),
            ), 
            id="Simple dataframe"
        ),
        pytest.param(
            pd.DataFrame(
                [[1], [2], [3]],
                columns=pd.Index(["first"]),
            ), 
            id="Single column datafram"
        ),
        pytest.param(
            pd.DataFrame(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                columns=pd.Index(["first", "second", "third"]),
                index=pd.Index(["a", "b", "c"], name="category")
            ),   
            id="Simple dataframe with index"
        ),
        pytest.param(
            pd.DataFrame(
                [[1, 2, 3, "a"], [4, 5, 6, "b"], [7, 8, 9, "c"], [10, 11, 12, "d"]],
                columns=pd.MultiIndex.from_tuples([("parent a", "child a"), ("parent a", "child b"), ("parent b", "child a"), ("parent c", "child a")], names=["lvl 1", "lvl 2"]),
                index=pd.MultiIndex.from_tuples([("row a", "sub a"), ("row a", "sub b"), ("row b", "sub a"), ("row c", "sub a")], names=["cat 1", "cat 2"]),
            ), 
            id="Complex dataframe"
        ),
        pytest.param(
            pd.DataFrame(
                [[1, 2], [4, 5]],
                columns=pd.MultiIndex.from_tuples([("col a", "child b", "subchild a"), ("col a", "child b", "subchild a")]),
                index=pd.MultiIndex.from_tuples([("row a", "child b", "subchild a"), ("row a", "child b", "subchild a")]),
            ), 
            id="Multiindex end with spanned"
        ),
        pytest.param(
            pd.DataFrame(
                [],
                columns=pd.Index(["first", "second", "third"]),
            ), 
            id="Empty datafram"
        ),
    ]
)
def test_with_html_table_no_error(df, tmpdir):

    sender = EmailSender(server=None, port=1234)
    msg = sender.get_message(
        sender="me@gmail.com",
        receiver="you@gmail.com",
        subject="Some news",
        html_body='The table {{my_table}}',
        body_tables={"my_table": df}
    )
    
    assert "multipart/alternative" == msg.get_content_type()

    #mime_text = msg.get_payload()[0]
    html = remove_extra_lines(msg.get_payload()[0].get_payload()).replace("=20", "").replace('"3D', "")
    #tmpdir.join("email.html").write(html)

    # TODO: Test the HTML is as required

    assert html