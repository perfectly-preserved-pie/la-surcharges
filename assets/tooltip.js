// customTooltip.js
function CustomTooltip() {}

CustomTooltip.prototype.init = function(params) {
    var eGui = document.createElement('div');
    eGui.innerHTML = params.column.getColDef().headerName;
    this.eGui = eGui;
};

CustomTooltip.prototype.getGui = function() {
    return this.eGui;
};

// Registering the custom tooltip
gridOptions.components = {
    customTooltip: CustomTooltip
};