var socket = io.connect(location.origin);
socket.on('connect', function() {
    socket.emit('my event', {data: 'Connected!'});
});
socket.on('message', function(data) {
    console.log(data, "PONG!");
});

function build_chart(canvas, plot_path) {
    const url = location.origin + "/get-data/" + plot_path;
    
    fetch(url)
    .then((resp) => resp.text())
    .then(function(data) {
        const dots = [];
        list = data.split(/\r?\n/);
        for (var i = 0; i < list.length; i++){
            if (!list[i]) continue;
            const vs = list[i].match(/[^ ]+/g).map(Number);
            const p = {}
            p.x = vs[0];
            p.y = vs[1];
            dots.push(p);
        }
        return new Chart(canvas, {
            type: 'scatter',
            data: {
                labels: ["Test"],
                datasets: [{
                    label: ["Test"],
                    data: dots,
                    showLine: true, 
                    borderColor: "rgba(255, 193, 7, 0.8)",
                    borderWidth: 1, 
                    backgroundColor: "rgba(255, 193, 7, 0.05)"
                }],
            },
            options: {
                responsive: true,
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: false
                        }
                    }],
                    xAxes: [{
                        ticks: {
                            beginAtZero: false
                        }
                    }]
                }
            }
        });
    })
    .catch(function(error) {
        console.log(error);
    }); 
}

function show_hide(evt){
    const filesList = evt.currentTarget.nextElementSibling;
    const projName = evt.currentTarget.innerHTML;
    const url = location.origin + "/list-files/" + projName;

    if (filesList.className.indexOf("w3-show") == -1){
        fetch(url)
        .then((resp) => resp.json())
        .then(function(files) {
            while (filesList.firstChild) {
                filesList.removeChild(filesList.firstChild);
            }
            return files.map(function(file) {
                const subdir = document.createElement('div'),
                    name   = document.createTextNode(file);
                subdir.className = "subdir";
                subdir.appendChild(name);

                const plot_path = projName + "/" + file;
                subdir.addEventListener('click', () => add_plot(plot_path, subdir));
                const headers = document.querySelectorAll(".card-header");
                for (const header of headers){
                    if (header.innerHTML == plot_path){
                        subdir.className += " opened";
                        break;
                    }
                }   
                filesList.appendChild(subdir);

            })
        })
        .catch(function(error) {
            console.log(error);
        });   
        filesList.className += " w3-show";
    } else {
        filesList.className = filesList.className.replace(" w3-show", "");
    }
    
}

function remove_card(card, plot_path){
    const dirs = document.querySelectorAll(".proj-expand");
    for (const d of dirs){
        if (plot_path.startsWith(d.innerHTML)){
            const subdirs = d.nextElementSibling.querySelectorAll(".subdir");
            for (const s of subdirs){
                if (plot_path.endsWith(s.innerHTML) && s.className.indexOf("opened") != -1){
                    s.className = s.className.replace(" opened", "");
                }
            }
        }
    } 
    card.parent_display.removeChild(card)
}

function add_plot(plot_path, subdir){
    if (subdir.className.indexOf("opened") != -1){
        return;
    }
    subdir.className += " opened";
    const plotDisplay = document.querySelector("#plot-display");
    const plotCard = document.querySelector("#plot-card-tmpl").content.querySelector(".plot-card");
    const card = document.importNode(plotCard, true);
    const header = card.querySelector(".card-header");
    const canvas = card.querySelector(".plot");
    const close = card.querySelector(".close-button");
    
    header.innerHTML = plot_path;
    card.parent_display = plotDisplay;
    build_chart(canvas, plot_path);
    close.addEventListener('click', () => remove_card(card, plot_path));
    plotDisplay.appendChild(card);
}