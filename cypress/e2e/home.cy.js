describe('Landing page button', () => {
  it('go on website', () => {
    cy.reload();
    cy.visit('https://silverbullets.rocks')
    cy.get('.btn_gioca').click()
    cy.go('back')
    cy.get('.btn_login').click()
    cy.go('back')
    cy.get('.btn_sign').click()
    cy.get('a:contains("Silver Bullets")').click();
  })



  

})