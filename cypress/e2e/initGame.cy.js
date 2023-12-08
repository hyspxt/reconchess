describe('Game initialization', () => {
    beforeEach(() => {
      cy.reload();
      cy.visit('https://silverbullets.rocks')
  
    })
    it('Select a certain game config', () => {
  
      cy.get('.btn_gioca').click()
      cy.get('.a_bot').click()
      cy.get('.a_human').click()
      cy.get('.a_bot').click()
      

      cy.get('#bot_1').click()
      cy.get('#bot_2').click()
      cy.get('#bot_3').click()
      cy.get('#bot_4').click()

      cy.get('select#frutta').select('n_15');
      cy.get('select#frutta').select('n_10');
      cy.get('select#frutta').select('n_5');
      cy.get('select#frutta').select('n_2-5');

      cy.get('.p_w').click()
      cy.get('.p_b').click()
     
    })
  
  })