for (let i = 0; i < document.getElementsByClassName("episodes-list")[0].children.length; i++)
{
    document.getElementsByClassName("episodes-list")[0].children[i].onclick = function()
    {
        if (document.querySelector(".episodes-list .active") != null){
            document.querySelector(".episodes-list .active").setAttribute("class", "");
        };
        document.getElementsByClassName("episodes-list")[0].children[i].setAttribute("class", "active");
        var video_id = document.getElementsByClassName("episodes-list")[0].children[i].attributes["id"].value;
        document.getElementById("my-video_html5_api").setAttribute("src", "/stream/" + video_id);
        document.getElementById("my-video_html5_api").setAttribute("poster", "/images/" + video_id);
        document.querySelector("picture.vjs-poster").children[0].setAttribute("src", "/images/" + video_id)
        return 0;
    }
}