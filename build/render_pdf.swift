import Foundation
import AppKit
import PDFKit

let source = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
let document = PDFDocument(url: source)!
for index in 0..<document.pageCount {
    let page = document.page(at: index)!
    let image = page.thumbnail(of: NSSize(width: 900, height: 1273), for: .mediaBox)
    let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
    let data = bitmap.representation(using: .png, properties: [:])!
    try data.write(to: output.appendingPathComponent("page_\(index+1).png"))
}
print("Rendered \(document.pageCount) pages")
