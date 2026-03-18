// please include below script tag in html befor including this file
// <script src="https://cdn.tiny.cloud/1/sozgxfg28gkwdz0upcdcf0pguivsi2gg0amwnz7c6iu4wsek/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>

// settings for tinymce
tinymce.init({
  selector: "textarea.editor",
  // content_css: "{% static 'styles/tinymce-defalut.css' %}",
  height: 380,
  plugins:
    "preview importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media template codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons",
  imagetools_cors_hosts: ["picsum.photos"],
  menubar: "file edit view insert format tools table help",
  toolbar:
    "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample | ltr rtl",
});
