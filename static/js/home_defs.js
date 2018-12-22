var socket = io.connect();
var file_socket = io.connect("/files");
var charts;

// function get_

function build_chart(canvas, plot_path) {
    const url = location.origin + "/get-data/" + plot_path;
    return fetch(url)
    .then((resp) => resp.text())
    .then(function(data) {
        const dots = [];
        const list = data.split(/\r?\n/);
        for (var i = 0; i < list.length; i++){
            if (!list[i]) continue;
            const vs = list[i].match(/[^\s,]+/g).map(Number);
            const p = {}
            p.x = vs[0];
            p.y = vs[1];
            dots.push(p);
        }
        return new Chart(canvas, {
            type: 'scatter',
            data: {
                labels: [],
                datasets: [{
                    label: [],
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
    console.log(url)

    socket.emit("list-files", projName);
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
                for (let i = 0; i < headers.length; i++){
                    if (headers[i].innerHTML == plot_path){
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

function remove_card(card, plot_path, tmp_func){
    file_socket.removeListener(plot_path, tmp_func);
    const dirs = document.querySelectorAll(".proj-expand");
    for (const d of dirs){
        if (plot_path.startsWith(d.innerHTML)){
            const subdirs = d.nextElementSibling.querySelectorAll(".subdir");
            for (const s of subdirs){
                s.classList.remove("opened")
            }
        }
    } 
    card.parent_display.removeChild(card)
}

function handle_sync(sync, path) {
    const nosync = sync.querySelector(".no-sync");
    sync.classList.toggle('sync');
    if (sync.classList.contains('sync')){
        nosync.classList.add("transparent");
        socket.emit('subscribe', path);
        
    } else {
        nosync.classList.remove("transparent");
        socket.emit('unsubscribe', path);
    } 
}

async function append_points(chart, points){
    const vs = points.match(/[^\s,]+/g).map(Number);
    const p = {};
    p.x = vs[0];
    p.y = vs[1];
    chart
    .then( (tmp) => {
        tmp.data.datasets[0].data.push(p);
        tmp.update();
    })
    .catch((error) => {
        console.log(error);
    });
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
    const sync = card.querySelector(".sync-button");

    header.innerHTML = plot_path;
    card.parent_display = plotDisplay;
    const chart = build_chart(canvas, plot_path);
    function tmp_func(points){
        append_points(chart, points);
    }
    file_socket.on(plot_path, tmp_func);
    close.addEventListener('click', () => remove_card(card, plot_path, tmp_func));
    sync.addEventListener('click', () => handle_sync(sync, plot_path));
    plotDisplay.appendChild(card);
}