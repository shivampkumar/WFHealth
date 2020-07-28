console.log("Service Worker Loaded...");

self.addEventListener("push", e => {
  const data = e.data.json();
  console.log("Push Recieved...");
  self.registration.showNotification(data.title, {
    body: "Coding straight for 30 min. Time to stretch those muscles",
    icon: "icon.jpg"
  });
});
