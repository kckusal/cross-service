
function addTag(tag_name) {
    const tagsContainer = document.getElementById('tags');
    const selectInput = document.getElementsByName("service-tags")[0];

    let tagName = (tag_name==="") ? prompt("Enter a tag name!") : tag_name;
    if (tagName === "" || tagName === null || tagName === undefined) return;
    
    // check if already present in the tags container there
    let currentTags = document.querySelectorAll(".tags > .tag");
    for(let i=0; i<currentTags.length; i++) {
        if (currentTags[i].innerHTML.toLowerCase() === tagName.toLowerCase()) {
            alert('Tag already added!');
            return;
        }
    };

    let div = document.createElement("div");
    div.classList.add('control');
    div.classList.add('tags');
    div.classList.add('has-addons');

    let tagText = document.createElement("span");
    tagText.classList.add('tag');
    tagText.classList.add('is-link');
    tagText.innerHTML = tagName;

    let tagDel = document.createElement("span");
    tagDel.classList.add('tag');
    tagDel.classList.add('is-delete');
    tagDel.style.cursor = "pointer";

    let selectOption = document.createElement("option");
    selectOption.value = tagName;
    selectOption.selected = true;
    selectInput.appendChild(selectOption);

    tagDel.onclick = function() {
        tagDel.parentNode.remove();
        selectOption.remove();
    };
    
    div.appendChild(tagText);
    div.appendChild(tagDel);

    tagsContainer.appendChild(div);
}


function showUserData(user_id) {
    const modal = document.getElementById("user-info-modal");
    
    const body = document.querySelectorAll("#user-info-modal > .modal-content")[0];

    const labels = body.querySelectorAll("label.label");
    labels.forEach((label) => {
        label.style.margin = "0";
        label.parentNode.classList.add('m-b-md');
    });
    

    const name = body.querySelectorAll(".name")[0];
    const bio = body.querySelectorAll(".bio")[0];
    const available = body.querySelectorAll(".available")[0];
    const email = body.querySelectorAll(".email")[0];
    const phone = body.querySelectorAll(".phone")[0];
    const address = body.querySelectorAll(".address")[0];

    $.ajax({
        url: "/user/" + user_id,
        data: {
        },
        dataType: 'json',
        success: function (data) {
            data = data.data;
            
            name.innerHTML = data.user.first_name + " " + data.user.last_name;
            
            console.log(data);

            bio.innerHTML = data.profile.bio;
            available.innerHTML = (data.profile.available === true) ? 'Yes': 'No';
            email.innerHTML = data.user.username;
            phone.innerHTML = data.profile.phone;
            address.innerHTML = data.profile.address;
        },
        error: function (err) {
            body.innerHTML = err.message;
        }
    });

    modal.classList.add('is-active');
}


function showSearchResultTab(clickedElem, targetIndex) {
    const togglers = document.querySelectorAll('.search-result-toggler');
    const targets = document.querySelectorAll('.search-result');
    
    if (clickedElem.classList.contains('is-active')) return;

    togglers.forEach((toggler) => {
        if (toggler.classList.contains('is-active')) toggler.classList.remove('is-active');
    });

    targets.forEach((targ) => {
        if (!targ.classList.contains('is-hidden')) targ.classList.add('is-hidden');
    });

    clickedElem.classList.add('is-active');
    targets[targetIndex].classList.remove('is-hidden');

}