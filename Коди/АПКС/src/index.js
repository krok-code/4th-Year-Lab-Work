function add(a, b) {
  return a + b;
}

function main() {
  console.log("Hello, World!");
}

if (require.main === module) {
  main();
}

module.exports = { add };
