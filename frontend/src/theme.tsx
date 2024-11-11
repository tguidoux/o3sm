import { extendTheme } from "@chakra-ui/react"

const disabledStyles = {
  _disabled: {
    backgroundColor: "ui.main",
  },
}

const theme = extendTheme({
  colors: {
    ui: {
      main: "#FF8C00",       // Vibrant orange
      secondary: "#FFF5E5",  // Soft peachy yellow
      success: "#FFD700",    // Golden yellow
      danger: "#FF4500",     // Deep orange-red
      light: "#FFFBEA",      // Very light creamy yellow
      dark: "#2C1B0E",       // Dark brownish-orange
      darkSlate: "#5C3B1E",  // Slate with a warm brown tone
      dim: "#D9A866"         // Muted amber
    },
  },
  components: {
    Button: {
      variants: {
        primary: {
          backgroundColor: "ui.main",
          color: "ui.light",
          _hover: {
            backgroundColor: "#FFF9F3",
          },
          _disabled: {
            ...disabledStyles,
            _hover: {
              ...disabledStyles,
            },
          },
        },
        danger: {
          backgroundColor: "ui.danger",
          color: "ui.light",
          _hover: {
            backgroundColor: "#E32727",
          },
        },
      },
    },
    Tabs: {
      variants: {
        enclosed: {
          tab: {
            _selected: {
              color: "ui.main",
            },
          },
        },
      },
    },
  },
})

export default theme
