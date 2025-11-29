// Stack Layout script for Adobe Illustrator
// Treats the last item of a selected group as the container and distributes other items horizontally with space-between logic.

function updateStackLayout(padding) {
    if (app.documents.length === 0) {
        alert('No document open.');
        return;
    }

    var doc = app.activeDocument;
    if (!doc.selection || doc.selection.length === 0) {
        alert('Select a group to update the stack layout.');
        return;
    }

    var target = doc.selection[0];
    if (!(target instanceof GroupItem)) {
        alert('The selection must be a GroupItem.');
        return;
    }

    if (target.pageItems.length < 2) {
        alert('The group needs at least one container and one item.');
        return;
    }

    // The bottom-most object (last in the stacking order) is used as the container (faceplate).
    var container = target.pageItems[target.pageItems.length - 1];

    // Collect all other items that will be distributed.
    var items = [];
    for (var i = 0; i < target.pageItems.length - 1; i++) {
        items.push(target.pageItems[i]);
    }

    // Extract container bounds. Illustrator returns [y1, x1, y2, x2],
    // where y1 is the top, x1 the left, y2 the bottom, and x2 the right.
    var cb = container.geometricBounds;
    var top = cb[0];
    var left = cb[1];
    var bottom = cb[2];
    var right = cb[3];

    var containerWidth = right - left;
    var containerHeight = top - bottom; // Y-axis is inverted (top has larger value than bottom).

    // Safe zone shrinks the container by the padding on all sides.
    var safeLeft = left + padding;
    var safeRight = right - padding;
    var safeTop = top - padding;      // Subtract padding because y decreases as we move down.
    var safeBottom = bottom + padding;

    var itemCount = items.length;
    if (itemCount === 0) {
        return;
    }

    // Calculate the spacing step. "Space Between" means the first item is at safeLeft,
    // the last at safeRight, with even spacing between remaining items.
    var step = itemCount > 1 ? (safeRight - safeLeft) / (itemCount - 1) : 0;

    // Vertical center line of the container. Because Illustrator's Y axis grows downward,
    // the center is still the average of top and bottom.
    var centerY = (top + bottom) / 2;

    for (var idx = 0; idx < itemCount; idx++) {
        var item = items[idx];
        var ib = item.geometricBounds;
        var iTop = ib[0];
        var iLeft = ib[1];
        var iBottom = ib[2];
        var iRight = ib[3];

        var itemWidth = iRight - iLeft;
        var itemHeight = iTop - iBottom; // Positive height since top > bottom.

        // Target center for this item.
        var targetX = safeLeft + step * idx;
        var targetY = centerY;

        // Illustrator positions use [left, top]. To place the center at (targetX, targetY),
        // shift left by half the width and shift the top down (toward positive y) by half the height.
        var newLeft = targetX - itemWidth / 2;
        var newTop = targetY + itemHeight / 2;

        item.position = [newLeft, newTop];
    }
}
