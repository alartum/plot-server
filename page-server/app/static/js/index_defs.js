function build_chart(canvas) {
    return new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
            datasets: [{
                label: '# of Votes',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255,99,132,1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
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
    build_chart(canvas);
    close.addEventListener('click', () => remove_card(card, plot_path));
    plotDisplay.appendChild(card);
}