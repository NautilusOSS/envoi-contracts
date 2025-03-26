import { program } from "./command.js"

console.log(process.argv);

program.parse(process.argv);
