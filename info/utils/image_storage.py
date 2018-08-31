import qiniu

# 需要填写你的 Access Key 和 Secret Key
access_key = 'kJ8wVO7lmFGsdvtI5M7eQDEJ1eT3Vrygb4SmR00E'
secret_key = 'rGwHyAvnlLK7rU4htRpNYzpuz0OHJKzX2O1LWTNl'
# 要上传的空间
bucket_name = 'infonews'


def upload_img(data):
    """上传文件"""
    q = qiniu.Auth(access_key, secret_key)
    key = None
    token = q.upload_token(bucket_name)
    ret, info = qiniu .put_data(token, key, data)
    if ret is not None:
        return ret.get("key")
    else:
        raise BaseException(info)



if __name__ == '__main__':
    with open("test.jpg", "rb") as f:
        img_bytes = f.read()
        try:
            file_name = upload_img(img_bytes)
            print(file_name)
        except BaseException as e:
            print(e)