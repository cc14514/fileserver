# 文件服务(HTTP)

<ul>
<li>上传地址 http://202.85.221.165/fileserver/upload/</li>
<li>下载地址 http://202.85.221.165/fileserver/get/文件id</li>
</ul>

<b>上传</b>
<p>输入:</p>
<p>模拟以下表单，即可完成附件上传，具体参数解释如下</p>

<form action="http://localhost:8000/fileserver/upload/" method="POST" enctype="multipart/form-data" >
        <!-- 上传附件的应用名，需要在后台注册 -->
        <p>appid:<input type="text" name="appid" value="test"/></p>
        <p>appkey:<input type="text" name="appkey" value="test"/></p>
        <p>id:<input type="text" name="id" value="" /></p>
        <!-- 附件类型，file / image 文件或 image，默认 image -->
        <p>file_type:<input type="text" name="file_type" value="image" /></p>
        <!-- # 是否加水印, 如果 file_type=image 则默认 true,可选值 true / false -->
        <p>watermark:<input type="text" name="watermark" value="true" /></p>
        <!-- 附件 -->
        <p>file:<input type="file" name="file" /></p>
        <button type="submit">submit</button>
</form>

<b>下载</b>
