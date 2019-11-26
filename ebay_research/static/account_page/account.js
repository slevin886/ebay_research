let alertDiv = document.getElementById('js_alert');
let messageDiv = document.getElementById('alert_message');

const switchToggle = {'none': 'block', 'block': 'none'};

function toggleRecurVisibility(){
  // Toggle visibility of recurring choice buttons
  // TODO: add hint of what to do i.e. select the search you would like to run on repeat
  let items = document.getElementsByClassName('hideRecurring');
  let displayMode = window.getComputedStyle(items[0]).getPropertyValue('display');
  displayMode = switchToggle[displayMode];
  for (let i = 0; i < items.length; i ++){
    items[i].style.display = displayMode;
  }
}


async function setRecurringSearch(searchId) {
  await axios.post(
    '/set_recurring_search',
    {'search_id': searchId},
  )
    .then((res) => {
      if (res.data.success) {
        sessionStorage.setItem("reloading", "true");
        sessionStorage.setItem("message", res.data.message);
        location.reload();
      } else {
        messageDiv.innerText = res.data.message;
        alertDiv.style.display = 'block';
        alertDiv.classList.add('show');
        alertDiv.classList.add('alert-danger');
      }
    })
    .catch((error) => {
      console.log(error);
      messageDiv.innerText = 'Whoops! Something went wrong, please try again later';
      alertDiv.style.display = 'block';
      alertDiv.classList.add('show');
      window.scrollTo(0, 0);
    });
  toggleRecurVisibility();
}


async function stopRecurringSearch(recurId) {
  await axios.post(
    '/stop_recurring_search',
    {'recur_id': recurId},
  )
    .then((res) => {
      messageDiv.innerText = res.data.message;
      alertDiv.style.display = 'block';
      alertDiv.classList.add('show');
      if (res.data.success) {
        alertDiv.classList.add('alert-success');
      } else {
        alertDiv.classList.add('alert-danger');
      }
      let row = document.getElementById('recur_' + recurId);
      row.parentNode.removeChild(row);
    })
    .catch((error) => {
      console.log(error);
      messageDiv.innerText = 'Whoops! Something went wrong, please try again later';
      alertDiv.style.display = 'block';
      alertDiv.classList.add('show');
      window.scrollTo(0, 0);
    });
  toggleRecurVisibility();
}

window.onload = function () {
  let reloading = sessionStorage.getItem("reloading");
  if (reloading) {
    messageDiv.innerText = sessionStorage.getItem("message");
    alertDiv.style.display = 'block';
    alertDiv.classList.add('show');
    alertDiv.classList.add('alert-success');
    window.scrollTo(0, 0);
    sessionStorage.removeItem("reloading");
    sessionStorage.removeItem("message");
  }
};