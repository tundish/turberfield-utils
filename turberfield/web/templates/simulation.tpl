<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{{info.get("title", "Turberfield")}}</title>
<link rel="stylesheet" href="/css/pure/base-min.css" />
<link rel="stylesheet" href="/css/pure/pure-min.css" media="screen" />
<link rel="stylesheet" href="/css/pure/grids-responsive-min.css" media="screen" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
% include("gainsborough_square.tpl")

<script type="text/javascript" src="/js/jquery-2.1.1.js"></script>
<script type="text/javascript" src="/js/knockout-3.2.0.js"></script>
<script type="text/javascript">

var viewModel = {
    debug: ko.observable(false),
    interval: ko.observable(2000),
    time: ko.observable(),
    items: ko.observableArray()
}

var checkStatus = function() {

    $.getJSON('/positions', function(data) {
        viewModel.debug(data.debug);
        viewModel.interval(data.interval);
        viewModel.time(data.time);
        viewModel.items(data.items);
    });

    setTimeout(checkStatus, viewModel.interval());

};

ko.applyBindings(viewModel);
checkStatus();

</script>

</body>
</html>
