# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=doc-string-missing

from paddle_serving_client import MultiLangClient
import functools
import sys
import time
import threading

client = MultiLangClient()
client.load_client_config(sys.argv[1])
client.connect(["127.0.0.1:9393"])

import paddle
test_reader = paddle.batch(
    paddle.reader.shuffle(
        paddle.dataset.uci_housing.test(), buf_size=500),
    batch_size=1)

complete_task_count = [0]
lock = threading.Lock()


def call_back(call_future, data):
    fetch_map = call_future.result()
    print("{} {}".format(fetch_map["price"][0], data[0][1][0]))
    with lock:
        complete_task_count[0] += 1


task_count = 0
for data in test_reader():
    future = client.predict(feed={"x": data[0][0]}, fetch=["price"], asyn=True)
    task_count += 1
    future.add_done_callback(functools.partial(call_back, data=data))

while complete_task_count[0] != task_count:
    time.sleep(0.1)