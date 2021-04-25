import React, { useContext } from "react";
import { useMapEvent } from "react-leaflet";
import { AppContext } from "../Context";

/**
 * Adds animation to the map on click, assuming that
 * user is not trying to create a tag
 * @returns null
 */
const Animation = () => {
  const { createTag } = useContext(AppContext);
  const map = useMapEvent("click", (click) => {
    if (createTag) {
      return;
    }
    map.setView(click.latlng, map.getZoom(), {
      animate: true,
    });
  });
  return null;
};

export { Animation };
