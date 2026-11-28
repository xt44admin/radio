export default {
  async fetch(request) {
    const response = await fetch("http://79.111.14.76:8002/beatdown");
    return new Response(response.body, {
      headers: {
        "Content-Type": "audio/aac",
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
};
