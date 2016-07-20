$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    //var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host  + window.location.pathname);
    //alert(window.location.host);
    //alert(window.location.pathname);
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        
        if(data.msg_type=='vote'){
            //alert("got message back vote");
            
            var divid = "#".concat(data.id)
            //alert(divid);
            var $mydiv = $(divid);
            var $score = $mydiv.find(".score");
            //alert($score.text());
            $score.text(data.score);
            //alert($score.text())

        }
        else{
        
        // create the element - division
        var ele = $("<div>",{class:"statement",id: data.id})
 		ele.attr("data-msgtype","reply");
 		ele.attr("data-msg_id",data.id);
	//alert(message.data);
	var media_left= $("<div>",{class:"media-left"})

	    media_left.append('<div class="vote comment-votes" style="float:left;" data-msg_id='+data.id+'> <div><i class="fa fa-chevron-up" name="upvote"></i></div><div class="score">0</div><div><i class="fa fa-chevron-down" name="downvote"></i></div> </div>')
	
	//ele.append($"<th rowspan="3"></th>")
	//ele.append($'<tr>')
        media_left.append(
            $("<span>",{class: "msgtext",text: data.message, style:"vertical-align:middle;"})
        )
	media_left.append('</br>')
        media_left.append(
            $("<span>",{class: "handle",text: "   -  ".concat(data.handle).concat("  -  "),style:"vertical-align:middle;"})
            
        )
	//ele.append($"</tr>")
        media_left.append(
            $("<span>",{class: "timestamp",text: data.timestamp,style:"vertical-align:middle;"})
        )
	ele.append(media_left)

    	var replyHtml = '<div class="reply-container"><ul class="buttons"><li><a href="javascript:void(0)" name="replyButton" class="replylink">reply</a></li></ul></div>'
		ele.append(replyHtml);
       
        // if not a reply append it to chat
        if(data.isreply==0){
            var chat = $("#chat")
            chat.append(ele)
        }
        else{
            var parentid = data.parentid
            //alert(parentid);
            var divid = "#".concat(parentid)
            //alert(divid);
            //var mydiv = $("#chat").find(divid)
            var mydiv = $(divid)
            //alert(mydiv.text())
            mydiv.append(ele)        
        }
        }
        // if a reply append it to div with id=data.parent_id
    };

    $("#chatmain").on("submit", function(event) {
	
        var message = {
            message: $('#message').val(),
            isreply: 0,
            parentid: 0,
            msg_type:'statement',
        }
	//alert("inside submit main");
        chatsock.send(JSON.stringify(message));
        $('#message').val('').focus();
        return false;
    });

    $("#chat").on("submit", ".replyforms",function(event) {
	

		
        var message = {
            message: $('#message'.concat($(this).data('msg_id'))).val(),
            isreply: 1,
            parentid: $(this).data('msg_id'),
            msg_type:'statement',
        }
	//alert("inside submit");
        chatsock.send(JSON.stringify(message));
        $('#message'.concat($(this).data('msg_id'))).val('').focus();


    var $mediaBody = $(this).parent().parent().parent();
    var $msgid = $mediaBody.parent().data().msg_id;
    var $formid = "chat".concat($msgid);
    var $inputid = "message".concat($msgid);
        
        var $mediaBody = $(this).parent().parent().parent();
		//$mediaBody.parent().find(".reply-container:first").append(newCommentForm);
        $commentForm = $mediaBody.find('.replyforms:first');
        if ($commentForm.attr('style') == null) {
            $commentForm.css('display', 'none')
        } else {
            $commentForm.removeAttr('style')
        }

        
        return false;
    });

    $('#chat').on("click",'i[name="upvote"]',function () {
        //alert("upvoted");
        var $voteDiv = $(this).parent().parent();
        var $msgid = $voteDiv.data().msg_id;
        //alert($msgid);
        var message = {
            msg_type: 'vote',
            value: 1,
            id: $msgid,
        }
        chatsock.send(JSON.stringify(message));
        //alert("done");
    });

    $('#chat').on("click",'i[name="downvote"]',function () {
        //alert("downvoted");
        var $voteDiv = $(this).parent().parent();
        var $msgid = $voteDiv.data().msg_id;
        //alert($msgid);
        var message = {
            msg_type: 'vote',
            value: -1,
            id: $msgid,
        }
        chatsock.send(JSON.stringify(message));
        //alert("done");
    });
    
});





$('#chat').on("click",'a[name="replyButton"]',function () {
    //alert("I pressed reply");
    var $mediaBody = $(this).parent().parent().parent();
    var $msgid = $mediaBody.parent().data().msg_id;
    var $formid = "chat".concat($msgid);
    var $inputid = "message".concat($msgid);
    
    var newCommentForm = '<form id="'.concat($formid).concat('" class="replyforms">\
                            <fieldset>\
                            <div class="form-group comment-group">\
                                <label for="commentContent" class="col-lg-2 control-label">Reply </label>\
                                <div class="col-lg-10">\
                                    <textarea class="form-control" rows="3" id="').concat($inputid).concat('"></textarea>\
                                    <span id="postResponse" class="text-success" style="display: none"></span>\
                                </div>\
                            </div>\
                            <div class="form-group">\
                                <div class="col-lg-10 col-lg-offset-2">\
                                    <button type="submit" class="btn btn-primary">Submit</button>\
                                </div>\
                            </div>\
                        </fieldset>\
                    </form>');
    
  
    if ($mediaBody.find('.replyforms').length == 0) {
        $mediaBody.parent().find(".reply-container:first").append(newCommentForm);
        var $form = $mediaBody.find('.replyforms');
        //alert($msgid);
        $form.attr("data-msg_id",$msgid);
        $form.attr("data-msgtype","reply");
        //$form.attr("id","chat".concat($msgid));
        //$form.submit(function (event) {
        //    submitEvent(event, $(this));
        //});
    } else {
        $commentForm = $mediaBody.find('.replyforms:first');
        if ($commentForm.attr('style') == null) {
            $commentForm.css('display', 'none')
        } else {
            $commentForm.removeAttr('style')
        }
    }


});




