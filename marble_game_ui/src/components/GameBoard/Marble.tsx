import SvgIcon from '@mui/material/SvgIcon';

// type definitions
type MarbleProps = {
    color?: 'B' | 'R' | 'W'  | ' ';
    size: number;
}

export function Marble({ color, size }: MarbleProps) {
  let htmlColor: string;

  switch (color) {
    case 'B':
      htmlColor = 'black';
      break;
    case 'R':
      htmlColor = 'red';
      break;
    case 'W':
      htmlColor = 'gray';
      break;
      default:
      //  return an empty SVG viewbox
      return (
          <SvgIcon
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
            sx={{height: size,  width: size}}
          />
      )
  }

  return (
    <SvgIcon
      htmlColor={htmlColor}
      viewBox="0 0 100 100"
      xmlns="http://www.w3.org/2000/svg"
      sx={{height: size, width: size}}
    >
     <circle cx="50" cy="50" r="50" />
    </SvgIcon>
  )
}
